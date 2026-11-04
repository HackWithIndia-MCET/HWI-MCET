import sqlite3
import os

db_paths = [
    r"C:\Users\saad uddin\.gemini\antigravity\scratch\hack-with-india-mcet\hwi_mcet.db",
    r"C:\Users\saad uddin\Desktop\mcet.hwi\hwi_mcet.db"
]

new_columns = [
    ("image_url", "TEXT DEFAULT ''"),
    ("registration_url", "TEXT DEFAULT ''"),
    ("link_label", "VARCHAR(100) DEFAULT 'Register Now'"),
    ("secondary_link_url", "TEXT DEFAULT ''"),
    ("secondary_link_label", "VARCHAR(100) DEFAULT ''"),
    ("badge_text", "VARCHAR(80) DEFAULT ''")
]

for p in db_paths:
    if not os.path.exists(p):
        print("Path does not exist, skipping:", p)
        continue
    
    conn = sqlite3.connect(p)
    c = conn.cursor()
    c.execute("PRAGMA table_info(sessions)")
    existing_cols = [r[1] for r in c.fetchall()]
    print(f"[{p}] Existing sessions cols: {existing_cols}")
    
    for col_name, col_type in new_columns:
        if col_name not in existing_cols:
            c.execute(f"ALTER TABLE sessions ADD COLUMN {col_name} {col_type}")
            print(f"  Added column: {col_name} to {p}")
        else:
            print(f"  Column already exists: {col_name}")
            
    conn.commit()
    conn.close()

print("Database schema migration completed successfully.")
