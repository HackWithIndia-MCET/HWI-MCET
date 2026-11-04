import sqlite3

db_path = r"C:\Users\saad uddin\.gemini\antigravity\scratch\hack-with-india-mcet\hwi_mcet.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM sessions")
count = c.fetchone()[0]

if count == 0:
    events = [
        (
            "HWI Flagship 36H Hackathon @ MCET",
            "Organizing Core",
            "MCET Tech Council & Industry Mentors",
            "Hackathon",
            "Day 1, 09:00 AM – Day 2, 09:00 PM",
            "MCET Newton Lab & Main Auditorium",
            "Offline",
            "",
            "The premier 36-hour inter-college builder sprint. Build impactful products across AI/ML, Web3, FinTech, and Open Innovation.",
            "Live Now",
            1,
            "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=600&q=80",
            "/register",
            "Register Team",
            "#about",
            "Rulebook",
            "₹1,00,000+ POOL"
        ),
        (
            "Keynote: Scalable Systems & Modern AI Engineering",
            "Guest Industry Architect",
            "VP of Engineering / Open Source Contributor",
            "Keynote",
            "Day 1, 11:30 AM – 12:30 PM",
            "Main Auditorium & Hybrid Stream",
            "Hybrid",
            "https://youtube.com/live",
            "Deep dive into building fault-tolerant distributed backends and production LLM orchestration with hands-on architectural walkthrough.",
            "Upcoming",
            2,
            "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=600&q=80",
            "/register",
            "Reserve Seat",
            "",
            "",
            "SEATS LIMITED"
        )
    ]

    c.executemany("""
        INSERT INTO sessions (
            title, speaker, speaker_title, category, time_slot, venue, mode, stream_url,
            description, status, order_num, image_url, registration_url, link_label,
            secondary_link_url, secondary_link_label, badge_text
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, events)
    conn.commit()
    print("Seeded 2 genuine events into sessions table.")
else:
    print(f"Sessions table already has {count} rows. Keeping existing data.")

conn.close()
