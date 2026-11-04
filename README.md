# 🚀 Hack with India — MCET Chapter | Dark Cyberpunk Community Hub

Official web portal and event platform for **Hack with India (HWI) — MCET Chapter**, redesigned with a **minimal, dark cyberpunk aesthetic** featuring electric red accents (`#FF2A2A`), editorial typography, geometric orbital graphics, and full FastAPI + SQLite backend integration.

---

## 🌐 Live Presentation Prototype URL
> **Public Prototype URL for Presentation:**  
> 🔗 **[https://f85c02466f3007.lhr.life](https://f85c02466f3007.lhr.life)**  
> **Local Server:** [http://127.0.0.1:8000](http://127.0.0.1:8000)

*Share this active URL with your mentors, judges, and presentation audience.*

---

## 🎨 Visual Identity & Reference Redesign
- **Canvas Aesthetic**: Pitch-dark background (`#08080A`) layered with subtle 56px geometric gridlines (`rgba(255, 255, 255, 0.025)`).
- **Brand Colors**:
  - 🔴 **Electric Red (`#FF2A2A`)**: Primary action buttons, badges, brand accents, and 3D geometric centerpiece.
  - ⚪ **Off-White (`#F4F4F5`, `#FAFAFA`)**: Editorial high-contrast headlines and primary content.
  - ⚫ **Dark Slate Card Canvas (`#101014`, `#16161B`)**: Fine borders (`rgba(255, 255, 255, 0.08)`).
- **Header**: Signature stylized red `h` lettermark, uppercase `MCET CHAPTER` tag, clean nav links (`About`, `Events`, `The team`, `Resources`), and `Join the chapter ↗` button.
- **Hero Section**:
  - Condensed grotesque headline: **`DON'T JUST THINK IT. BUILD IT.`** with `"BUILD IT."` in bright electric red.
  - Copy: *"Big ideas start with curious people. A campus community for the builders, the breakers, and everyone ready to make their first move."*
  - Dual CTAs: Solid red `Find your people ↗` button and `Explore events ↓`.
  - Right Column: CSS/SVG 8-spoke 3D-shaded star/asterisk with dual wireframe elliptical orbits, rotating subtly and respecting `prefers-reduced-motion`.
- **Marquee Ticker Strip**: Full-width bold red strip (`#FF2A2A`) smoothly repeating: `CODE ✱ CREATE ✱ COLLABORATE ✱ HACKWITHINDIA ✱ MCET CHAPTER ✱ ...`.
- **Authentic Content**: Removed all fabricated claims, fake testimonials, and phantom statistics. Included clean, honest empty states for events, announcements, and team announcements.

---

## 🗺️ Architecture Mapping (Directly From Your Plan Blueprint)

| Blueprint Diagram Node | Feature Implemented in Portal |
| :--- | :--- |
| **`User * team` & `Google Form`** | Multi-channel registration: Direct high-vibe web form + Google Form sync option. |
| **`Auth - SupaAuth / Clerk / Firebase`** | Interactive Auth simulation switcher allowing 1-click toggling between SupaAuth, Clerk, and Firebase providers. |
| **`regester team` ➔ `u get allotment, guide to do nxt...`** | Instant Allotment engine allocating: Team ID, Lab & Desk (e.g. Newton Hub Desk 03), Assigned Faculty & Alumni Mentor, Wi-Fi keys, and step-by-step checklist. |
| **`Sessions` (Offline, Hybrid - games, leadership, dashboard)** | Interactive sessions hub featuring: Leadership talks with Google/Razorpay speakers, offline workshops, hybrid streams, and live status radar. |
| **`Wining Parameter` & `point system`** | Standardized 100-Point Rubric: Innovation (25%), Technical Depth (25%), Feasibility & Impact (20%), UI/UX (15%), Pitch (15%) + Interactive Simulator + Live Leaderboard. |
| **`Games` (Red Arrow)** | Playable mid-hack challenges: Speed Bug Hunter (Async deadlock / mutable defaults), Cyber Trivia, and Vibe Typing Dash with live WPM meter and score boosts. |
| **`Feedback from student & guest ppl`** | Multi-role review desk for students, guest evaluators, and mentors with star ratings and categorized tags. |
| **`Summarize feedbacks`** | AI Sentiment & Feedback Synthesizer computing satisfaction metrics, top strengths, and action items for organizers. |
| **`Pics, notifications, baners ..of event` ➔ `Add in Blog of HWI`** | Live broadcast feed & photo gallery stream with real-time announcements, urgent notices, and photo highlights. |
| **`Admin Panel` ➔ `Sport Registrations` & `Number of presenties`** | Organizer control deck featuring: Walk-in Spot Registration desk, 1-click attendance toggle (`Number of presenties` tracker), and Jury score recording. |

---

## 🛠️ Tech Stack
- **Backend:** Python 3.14+, FastAPI, Starlette, Uvicorn, SQLAlchemy ORM
- **Database:** SQLite (`hwi_mcet.db`) with automatic pre-seeded realistic campus data
- **Frontend:** Jinja2 templates, Tailwind CSS, FontAwesome/Lucide, Canvas Confetti
- **Tunneling:** OpenSSH tunnel integration for instant public HTTPS sharing

---

## ⚡ How to Run Locally

1. **Navigate to the project folder:**
   ```powershell
   cd "C:\Users\saad uddin\.gemini\antigravity\scratch\hack-with-india-mcet"
   ```

2. **Launch server with automatic prototype tunnel:**
   ```powershell
   python run.py --tunnel
   ```

3. **Or launch local server only:**
   ```powershell
   python run.py
   ```
   Open `http://127.0.0.1:8000` in your web browser.


---

## 👥 Official Chapter Leadership Team 2026

> *“Great things are never done by one person; they are done by a team of people.”*  
> **HackWithIndia × MCET | Methodist College of Engineering and Technology**

### 🌟 Core Leadership Team
| S. No. | Position / Domain | Name |
| :---: | :--- | :--- |
| 1 | **President** | Zaid Bin Khalid |
| 2 | **Organizer** | Bhukya Vinay Kumar |
| 3 | **Co-Organizer** | Likitha Mahankali |
| 4 | **Chief Coordinator** | Syed Razi Hasan Razvi |
| 5 | **Vice Chief Coordinator** | Syed Nooruddin Hussaini |
| 6 | **General Secretary** | Mohammed Abdul Raheem |
| 7 | **Secretary** | Abida Begum |
| 8 | **Vice Secretary** | Manha Fatima |

### 🛠️ Functional Leads
| S. No. | Position / Domain | Name |
| :---: | :--- | :--- |
| 1 | **Technical Lead** | Pavan Yadav |
| 2 | **Vice Technical Lead** | Shaik Saaduddin |
| 3 | **Development Lead** | Kancharla Anand Kumar |
| 4 | **Social Media & Content Lead** | Sanda Varun Sagar |
| 5 | **Designing Lead** | Mirza Alamdar Abbas Hussain |
| 6 | **Co-Designing Lead** | Tejas A |
| 7 | **Content Creation Lead** | Mohammed Zun Nurain Khan |
| 8 | **Editor** | Chinthala Dimple Kumar |
| 9 | **PR & Outreach Lead** | Manavala Vishnu Vardhan |
| 10 | **Event Management & Sponsorship Lead** | Mandumula Sneha |
| 11 | **Vice Event Management Lead** | Shaik Md Aman |
| 12 | **Women Ambassador** | M. Shanthimani |
| 13 | **Community & Membership Lead** | Syed Riyaan Hussain |
