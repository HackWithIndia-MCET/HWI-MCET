import sqlite3

conn = sqlite3.connect(r'C:\Users\saad uddin\.gemini\antigravity\scratch\hack-with-india-mcet\hwi_mcet.db')
c = conn.cursor()
c.execute("PRAGMA table_info(sessions)")
cols = [r[1] for r in c.fetchall()]
print('sessions table columns:', cols)
c.execute("SELECT COUNT(*) FROM sessions")
print('sessions count:', c.fetchone()[0])
c.execute("SELECT * FROM sessions")
rows = c.fetchall()
for r in rows:
    print(' ', r)
conn.close()
