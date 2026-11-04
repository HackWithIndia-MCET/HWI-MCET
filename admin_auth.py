"""
Admin Authentication & Security Module for Hack With India x MCET
Supports Argon2id password hashing, JWT HttpOnly sessions, IP rate limiting, and Audit Logging.
"""
import os
import time
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from fastapi import Request, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

from database import get_db
from models import AdminUser, AdminAuditLog

# Secret key for JWT signing
JWT_SECRET = os.getenv("ADMIN_JWT_SECRET", "hwi-mcet-cyber-supersecret-jwt-key-2026-v2")
JWT_ALGORITHM = "HS256"
SESSION_EXPIRE_HOURS = 8

# Password Hasher (Argon2id)
ph = PasswordHasher()

# IP-based Failed Login Rate Limiter (Max 5 failed attempts per 60 seconds)
# Format: {ip: [timestamp1, timestamp2, ...]}
FAILED_ATTEMPTS: Dict[str, list] = {}
RATE_LIMIT_MAX_ATTEMPTS = 5
RATE_LIMIT_WINDOW_SECONDS = 60

def hash_password(password: str) -> str:
    """Hashes a plain-text password using Argon2id."""
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against an Argon2id or bcrypt hash."""
    if not hashed_password or not plain_password:
        return False
    # Check Argon2
    if hashed_password.startswith("$argon2"):
        try:
            return ph.verify(hashed_password, plain_password)
        except (VerifyMismatchError, VerificationError):
            return False
    # Fallback to bcrypt if stored as bcrypt
    if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
        try:
            import bcrypt
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False
    return False

def check_rate_limit(ip: str) -> Tuple[bool, int]:
    """
    Checks if an IP has exceeded failed login attempts.
    Returns (is_blocked, remaining_seconds).
    """
    now = time.time()
    attempts = FAILED_ATTEMPTS.get(ip, [])
    # Filter attempts within the time window
    attempts = [t for t in attempts if now - t < RATE_LIMIT_WINDOW_SECONDS]
    FAILED_ATTEMPTS[ip] = attempts
    if len(attempts) >= RATE_LIMIT_MAX_ATTEMPTS:
        remaining = int(RATE_LIMIT_WINDOW_SECONDS - (now - attempts[0]))
        return True, max(1, remaining)
    return False, 0

def record_failed_attempt(ip: str):
    """Records a failed login attempt for the IP."""
    now = time.time()
    attempts = FAILED_ATTEMPTS.get(ip, [])
    attempts.append(now)
    FAILED_ATTEMPTS[ip] = attempts

def reset_rate_limit(ip: str):
    """Resets rate limit counter on successful login."""
    if ip in FAILED_ATTEMPTS:
        del FAILED_ATTEMPTS[ip]

def create_admin_token(username: str) -> str:
    """Generates an 8-hour signed JWT session token."""
    expire = datetime.utcnow() + timedelta(hours=SESSION_EXPIRE_HOURS)
    payload = {
        "sub": username,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_admin_token(token: str) -> Optional[str]:
    """Decodes and validates JWT token, returning username or None."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except Exception:
        return None

def get_client_ip(request: Request) -> str:
    """Retrieves real client IP considering forward headers."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

def log_admin_action(db: Session, username: str, action: str, details: str, ip: str = ""):
    """Appends an entry to admin_logs table."""
    try:
        log_entry = AdminAuditLog(
            admin_username=username,
            action=action,
            details=details,
            ip_address=ip,
            created_at=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        print(f"[!] Failed to log admin action: {e}")

def get_current_admin(request: Request, db: Session = Depends(get_db)) -> AdminUser:
    """
    FastAPI dependency for administrative routes.
    Checks cookie `hwi_admin_token` or `Authorization: Bearer <token>` header.
    Raises HTTPException 401 for API endpoints or redirects to /admin/login for HTML pages.
    """
    token = request.cookies.get("hwi_admin_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    is_api = request.url.path.startswith("/api/")

    if not token:
        if is_api:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token missing. Please log in."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                headers={"Location": "/admin/login"}
            )

    username = decode_admin_token(token)
    if not username:
        if is_api:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session token expired or invalid. Please re-authenticate."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                headers={"Location": "/admin/login"}
            )

    admin = db.query(AdminUser).filter(AdminUser.username == username, AdminUser.is_active == True).first()
    if not admin:
        if is_api:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Administrator account not found or deactivated."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                headers={"Location": "/admin/login"}
            )

    return admin

def initialize_default_admin(db: Session):
    """
    Checks for administrator accounts in Supabase database.
    Credentials live exclusively in the database (admin_users table).
    """
    existing_count = db.query(AdminUser).count()
    if existing_count == 0:
        init_user = os.getenv("ADMIN_INIT_USERNAME")
        init_pass = os.getenv("ADMIN_INIT_PASSWORD")
        if init_user and init_pass:
            pwd_hash = hash_password(init_pass)
            initial_admin = AdminUser(
                username=init_user.strip(),
                password_hash=pwd_hash,
                created_at=datetime.utcnow(),
                is_active=True
            )
            db.add(initial_admin)
            db.commit()
            print(f"[SECURITY] Admin account initialized from environment: '{init_user}'")
        else:
            print("[SECURITY] Note: No admin users in database. Create via Supabase admin_users table.")
    else:
        print(f"[SECURITY] Verified administrator account in Supabase ({existing_count} active admin).")
