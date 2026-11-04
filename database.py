"""
Database configuration for Hack With India @ MCET Campus
Supports both Supabase PostgreSQL (via DATABASE_URL in .env) and local SQLite fallback.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_PATH = os.path.join(BASE_DIR, "hwi_mcet.db")

# Read and sanitize DATABASE_URL from environment
raw_url = os.getenv("DATABASE_URL")

if raw_url:
    # Strip any accidental whitespace, newlines, or quotes copied into Vercel
    clean_url = raw_url.strip().strip('"').strip("'")
    if clean_url.startswith("postgres://"):
        clean_url = clean_url.replace("postgres://", "postgresql://", 1)
    DATABASE_URL = clean_url
else:
    DATABASE_URL = f"sqlite:///{DB_PATH}"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Safe Engine Initialization with graceful fallback
try:
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True
    )
except Exception as e:
    print(f"[WARN] Failed to initialize engine with DATABASE_URL, falling back to SQLite: {e}")
    DATABASE_URL = f"sqlite:///{DB_PATH}"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
