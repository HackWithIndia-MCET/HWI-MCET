import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

src_base = r'C:\Users\saad uddin\.gemini\antigravity\scratch\hack-with-india-mcet'
dst_base = r'C:\Users\saad uddin\Desktop\mcet.hwi'

print(f"Syncing from {src_base} to {dst_base}...")

files_to_sync = [
    '.env',
    '.env.example',
    '.gitignore',
    'models.py',
    'database.py',
    'admin_auth.py',
    'admin_routes.py',
    'migrate_sqlite_to_supabase.py',
    'main.py',
    'README.md',
    'fix_sequences.py',
    'serve_48hr.py',
    'hwi_mcet.db',
    'hwi_mcet.db.backup',
    os.path.join('templates', 'events.html'),
    os.path.join('templates', 'index.html'),
    os.path.join('templates', 'register.html'),
    os.path.join('templates', 'feedback.html'),
]

for rel in files_to_sync:
    s = os.path.join(src_base, rel)
    d = os.path.join(dst_base, rel)
    if os.path.exists(s):
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)
        print(f"  + Synced file: {rel} ({os.path.getsize(d):,} bytes)")

# Sync entire templates/admin/ directory
admin_src = os.path.join(src_base, 'templates', 'admin')
admin_dst = os.path.join(dst_base, 'templates', 'admin')
if os.path.exists(admin_src):
    os.makedirs(admin_dst, exist_ok=True)
    for f in os.listdir(admin_src):
        sf = os.path.join(admin_src, f)
        df = os.path.join(admin_dst, f)
        if os.path.isfile(sf):
            shutil.copy2(sf, df)
            print(f"  + Synced admin template: templates/admin/{f}")

print("[*] All admin dashboard, database, and backend files successfully synchronized to Desktop.")
