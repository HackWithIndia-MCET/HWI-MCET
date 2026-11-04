import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
db_url = os.getenv("DATABASE_URL")

conn = psycopg2.connect(db_url)
cur = conn.cursor()

tables = [
    "admin_users",
    "admin_logs",
    "team_members",
    "site_settings",
    "teams",
    "sessions",
    "feedbacks",
    "blogs",
    "games"
]

print("[*] Synchronizing PostgreSQL sequences to match highest existing ID...")
for table in tables:
    try:
        cur.execute(f"SELECT COALESCE(MAX(id), 0) FROM {table}")
        max_id = cur.fetchone()[0]
        seq_name = f"{table}_id_seq"
        if max_id > 0:
            cur.execute(f"SELECT setval('{seq_name}', {max_id}, true)")
            cur.execute(f"SELECT last_value, is_called FROM {seq_name}")
            row = cur.fetchone()
            print(f"[OK] {table}: max_id={max_id} -> seq '{seq_name}' set to {row[0]} (is_called={row[1]})")
        else:
            cur.execute(f"SELECT setval('{seq_name}', 1, false)")
            print(f"[OK] {table}: empty table (max_id=0) -> seq '{seq_name}' set to 1 (is_called=False)")
    except Exception as e:
        conn.rollback()
        print(f"[!] Warning on table {table}: {e}")
        continue
    conn.commit()

conn.close()
print("[*] All sequences updated successfully!")
