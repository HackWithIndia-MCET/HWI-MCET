"""
Migration script from local SQLite (hwi_mcet.db) to Supabase PostgreSQL.
Preserves existing authentic records with exact primary keys.
Strictly Zero Seeded Data constraint honored.
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, DB_PATH
import models

def migrate_to_supabase(supabase_db_url: str):
    print("[*] Connecting to local SQLite database...")
    sqlite_engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
    SqliteSession = sessionmaker(bind=sqlite_engine)
    sqlite_db = SqliteSession()

    print("[*] Connecting to Supabase PostgreSQL...")
    supabase_engine = create_engine(supabase_db_url, pool_pre_ping=True)
    SupabaseSession = sessionmaker(bind=supabase_engine)
    supabase_db = SupabaseSession()

    print("[*] Creating all tables in Supabase PostgreSQL if not exist...")
    Base.metadata.create_all(bind=supabase_engine)
    print("  [OK] Tables created in Supabase.")

    # 1. Admin Users
    admin_users = sqlite_db.query(models.AdminUser).all()
    print(f"[*] Migrating {len(admin_users)} Admin User(s)...")
    for u in admin_users:
        if not supabase_db.query(models.AdminUser).filter(models.AdminUser.username == u.username).first():
            supabase_db.add(models.AdminUser(
                id=u.id,
                username=u.username,
                password_hash=u.password_hash,
                created_at=u.created_at,
                last_login=u.last_login,
                is_active=u.is_active
            ))

    # 2. Teams (Registrations)
    teams = sqlite_db.query(models.TeamRegistration).all()
    print(f"[*] Migrating {len(teams)} authentic Team Registration(s)...")
    for t in teams:
        if not supabase_db.query(models.TeamRegistration).filter(models.TeamRegistration.registration_id == t.registration_id).first():
            supabase_db.add(models.TeamRegistration(
                id=t.id,
                registration_id=t.registration_id,
                team_name=t.team_name,
                lead_name=t.lead_name,
                lead_email=t.lead_email,
                lead_phone=t.lead_phone,
                college=t.college,
                track=t.track,
                members=t.members,
                mode=t.mode,
                is_spot_registration=t.is_spot_registration,
                is_present=t.is_present,
                status=t.status,
                event_id=t.event_id,
                event_title=t.event_title,
                lab_allotment=t.lab_allotment,
                mentor_name=t.mentor_name,
                mentor_contact=t.mentor_contact,
                project_title=t.project_title,
                project_repo=t.project_repo,
                score_innovation=t.score_innovation,
                score_technical=t.score_technical,
                score_impact=t.score_impact,
                score_ui_ux=t.score_ui_ux,
                score_pitch=t.score_pitch,
                total_score=t.total_score,
                created_at=t.created_at
            ))

    # 3. Feedbacks
    feedbacks = sqlite_db.query(models.FeedbackItem).all()
    print(f"[*] Migrating {len(feedbacks)} Feedback record(s)...")
    for fb in feedbacks:
        if not supabase_db.query(models.FeedbackItem).filter(models.FeedbackItem.id == fb.id).first():
            supabase_db.add(models.FeedbackItem(
                id=fb.id,
                author_name=fb.author_name,
                role=fb.role,
                rating=fb.rating,
                category=fb.category,
                comment=fb.comment,
                sentiment=fb.sentiment,
                is_visible=fb.is_visible,
                created_at=fb.created_at
            ))

    # 4. Announcements / Blogs
    blogs = sqlite_db.query(models.BlogItem).all()
    print(f"[*] Migrating {len(blogs)} Announcement(s)...")
    for b in blogs:
        if not supabase_db.query(models.BlogItem).filter(models.BlogItem.id == b.id).first():
            supabase_db.add(models.BlogItem(
                id=b.id,
                title=b.title,
                category=b.category,
                image_url=b.image_url,
                author=b.author,
                summary=b.summary,
                content=b.content,
                pinned=b.pinned,
                created_at=b.created_at
            ))

    # 5. Site Settings
    settings = sqlite_db.query(models.SiteSettings).all()
    print(f"[*] Migrating {len(settings)} Site Setting(s)...")
    for s in settings:
        if not supabase_db.query(models.SiteSettings).filter(models.SiteSettings.key == s.key).first():
            supabase_db.add(models.SiteSettings(
                id=s.id,
                key=s.key,
                value=s.value,
                description=s.description,
                updated_at=s.updated_at
            ))

    # 6. Admin Logs
    logs = sqlite_db.query(models.AdminAuditLog).all()
    print(f"[*] Migrating {len(logs)} Audit Log(s)...")
    for l in logs:
        if not supabase_db.query(models.AdminAuditLog).filter(models.AdminAuditLog.id == l.id).first():
            supabase_db.add(models.AdminAuditLog(
                id=l.id,
                admin_username=l.admin_username,
                action=l.action,
                details=l.details,
                ip_address=l.ip_address,
                created_at=l.created_at
            ))

    supabase_db.commit()
    sqlite_db.close()
    supabase_db.close()
    print("[SUCCESS] Full SQLite -> Supabase PostgreSQL migration completed successfully!")

if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if not url:
        print("Usage: python migrate_sqlite_to_supabase.py <SUPABASE_POSTGRES_URL>")
        if len(sys.argv) > 1:
            url = sys.argv[1]
        else:
            sys.exit(1)
    migrate_to_supabase(url)
