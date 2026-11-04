"""
Hack With India @ MCET Campus - FastAPI Backend & Vibecoding Hub
Equipped with Real-time Allotments, Winning Parameters, Sessions, Leaderboard,
Games Arena, Dynamic Feedback Summarizer, Live Blog, and Organizer Admin Panel.
"""
import json
import random
import os
import re
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import engine, get_db, Base
import models

# Path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Initialize Database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hack With India @ MCET Campus",
    description="Official Vibecoding Hackathon Portal with Realtime Allotment, Hybrid Sessions, Point System, and Organizer Dashboard",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and Templates mounting
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Labs and Mentors Pool for Automatic Smart Allotment
LABS_POOL = [
    "Newton Innovation Center - Bay A (Desks 01-10)",
    "Newton Innovation Center - Bay B (Desks 11-20)",
    "Turing Computing Lab - Bay 1 (Tables 01-08)",
    "Turing Computing Lab - Bay 2 (Tables 09-16)",
    "Aryabhata AI & Robotics Lab - Pod Alpha",
    "Aryabhata AI & Robotics Lab - Pod Beta",
    "Ramanujan High Performance Center - Desk 05",
    "Kalam Open Innovation Sandbox - Hub 3"
]

MENTORS_POOL = [
    {"name": "Dr. Arvind Swaminathan", "contact": "arvind.swamy@mcet.edu.in", "domain": "AI & Agentic Systems"},
    {"name": "Prof. Sneha Verma", "contact": "sneha.verma@mcet.edu.in", "domain": "Fullstack & Cloud Architecture"},
    {"name": "Karthik Rajan (Alumni, Staff Eng @ Google)", "contact": "karthik.r@hwi-mentor.org", "domain": "Scalable Systems & Web3"},
    {"name": "Ananya Sen (FinTech Lead @ Razorpay)", "contact": "ananya.sen@hwi-mentor.org", "domain": "FinTech & Security"},
    {"name": "Dr. M. S. Sundaram", "contact": "sundaram.ms@mcet.edu.in", "domain": "GreenTech & Embedded IoT"}
]

# Startup Event
@app.on_event("startup")
def on_startup():
    from database import SessionLocal
    import admin_auth
    db = SessionLocal()
    try:
        admin_auth.initialize_default_admin(db)
    finally:
        db.close()




# Root Favicon Route
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    fav_path = os.path.join(STATIC_DIR, "favicon.ico")
    if os.path.exists(fav_path):
        return FileResponse(fav_path, media_type="image/x-icon")
    raise HTTPException(status_code=404, detail="Favicon not found")


# Web UI Route - Home Page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# Web UI Route - Dedicated Team-Based Registration Page
@app.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    event_id: Optional[int] = None,
    event_title: Optional[str] = None,
    db: Session = Depends(get_db)
):
    sessions = db.query(models.SessionItem).filter(
        models.SessionItem.is_published == True,
        models.SessionItem.registration_open == True
    ).order_by(models.SessionItem.order_num.asc()).all()
    
    # If event_id is supplied but not event_title, look it up
    if event_id and not event_title:
        ev = db.query(models.SessionItem).filter(models.SessionItem.id == event_id).first()
        if ev:
            event_title = ev.title

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "selected_event_id": event_id,
            "selected_event_title": event_title or "",
            "sessions": sessions
        }
    )


# Web UI Route - Dedicated Events Page
@app.get("/events", response_class=HTMLResponse)
async def events_page(request: Request, db: Session = Depends(get_db)):
    events = db.query(models.SessionItem).filter(
        models.SessionItem.is_published == True
    ).order_by(models.SessionItem.order_num.asc(), models.SessionItem.id.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="events.html",
        context={
            "events": events
        }
    )


# Web UI Route - Dedicated Feedback & Attendee Voice Page
@app.get("/feedback", response_class=HTMLResponse)
async def feedback_page(request: Request, db: Session = Depends(get_db)):
    feedbacks = db.query(models.FeedbackItem).filter(
        models.FeedbackItem.is_visible == True
    ).order_by(models.FeedbackItem.created_at.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="feedback.html",
        context={
            "feedbacks": feedbacks
        }
    )


# API: Live Dashboard Statistics
@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total_registered = db.query(models.TeamRegistration).count()
    present_count = db.query(models.TeamRegistration).filter(models.TeamRegistration.is_present == True).count()
    spot_count = db.query(models.TeamRegistration).filter(models.TeamRegistration.is_spot_registration == True).count()
    offline_count = db.query(models.TeamRegistration).filter(models.TeamRegistration.mode == "Offline").count()
    hybrid_count = db.query(models.TeamRegistration).filter(models.TeamRegistration.mode == "Hybrid").count()
    
    avg_score = db.query(func.avg(models.TeamRegistration.total_score)).filter(models.TeamRegistration.total_score > 0).scalar() or 0.0
    feedback_count = db.query(models.FeedbackItem).count()
    sessions_count = db.query(models.SessionItem).count()

    return {
        "total_registered": total_registered,
        "present_count": present_count,
        "spot_count": spot_count,
        "offline_count": offline_count,
        "hybrid_count": hybrid_count,
        "avg_score": round(float(avg_score), 1),
        "feedback_count": feedback_count,
        "sessions_count": sessions_count
    }


# API: Register Team (Regular Web & Dedicated Team Page)
@app.post("/api/register")
def register_team(data: models.TeamCreate, db: Session = Depends(get_db)):
    # 1. Validate team name
    clean_team_name = data.team_name.strip() if data.team_name else ""
    if len(clean_team_name) < 2:
        raise HTTPException(status_code=400, detail="Team name must be at least 2 characters long.")

    # 2. Check duplicate team name (case-insensitive)
    existing = db.query(models.TeamRegistration).filter(
        func.lower(models.TeamRegistration.team_name) == clean_team_name.lower()
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Team '{clean_team_name}' is already registered! Please choose a unique name.")

    # 3. Validate leader information
    clean_lead_name = data.lead_name.strip() if data.lead_name else ""
    if len(clean_lead_name) < 2:
        raise HTTPException(status_code=400, detail="Team leader name is required (at least 2 characters).")

    clean_lead_email = data.lead_email.strip().lower() if data.lead_email else ""
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", clean_lead_email):
        raise HTTPException(status_code=400, detail="Please enter a valid team leader email address.")

    clean_lead_phone = data.lead_phone.strip() if data.lead_phone else ""
    digits = re.sub(r"[^0-9]", "", clean_lead_phone)
    if len(digits) < 7:
        raise HTTPException(status_code=400, detail="Please enter a valid leader phone number (at least 7 digits).")

    # 4. Validate team size & member information
    raw_members = data.members or []
    # Team size limit: Max 4 members total (1 leader + up to 3 additional members)
    if len(raw_members) > 3:
        raise HTTPException(status_code=400, detail="Maximum team size exceeded. A team may have at most 4 members (1 leader + up to 3 members).")

    emails_seen = {clean_lead_email}
    processed_members = []
    
    # Leader is member #1
    processed_members.append({
        "name": f"{clean_lead_name} (Lead)",
        "email": clean_lead_email,
        "role": "Team Leader"
    })

    for idx, m in enumerate(raw_members, start=2):
        if isinstance(m, dict):
            m_name = m.get("name", "").strip()
            m_email = m.get("email", "").strip().lower()
            m_role = m.get("role", f"Member {idx}").strip()
            if m_name:
                if m_email:
                    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", m_email):
                        raise HTTPException(status_code=400, detail=f"Member {idx} ({m_name}) has an invalid email address: {m_email}")
                    if m_email in emails_seen:
                        raise HTTPException(status_code=400, detail=f"Duplicate email '{m_email}' found in team roster. Each member must have a distinct email.")
                    emails_seen.add(m_email)
                processed_members.append({"name": m_name, "email": m_email, "role": m_role})
        elif isinstance(m, str) and m.strip():
            processed_members.append({"name": m.strip(), "email": "", "role": f"Member {idx}"})

    # Associate event if passed
    project_label = ""
    if data.event_title:
        project_label = f"Event: {data.event_title.strip()}"
    elif data.event_id:
        ev = db.query(models.SessionItem).filter(models.SessionItem.id == data.event_id).first()
        if ev:
            project_label = f"Event: {ev.title}"

    # Generate Registration ID
    count = db.query(models.TeamRegistration).count() + 1
    reg_id = f"HWI-MCET-{100 + count}"

    # Smart Allotment of Lab and Mentor
    lab = LABS_POOL[(count - 1) % len(LABS_POOL)]
    mentor = MENTORS_POOL[(count - 1) % len(MENTORS_POOL)]

    new_team = models.TeamRegistration(
        registration_id=reg_id,
        team_name=clean_team_name,
        lead_name=clean_lead_name,
        lead_email=clean_lead_email,
        lead_phone=clean_lead_phone,
        college=data.college.strip() if data.college else "MCET Campus",
        track=data.track.strip() if data.track else "AI & Intelligent Systems",
        members=json.dumps(processed_members),
        mode=data.mode or "Offline",
        is_spot_registration=bool(data.is_spot_registration),
        is_present=True if data.is_spot_registration else False,
        status="Checked-In" if data.is_spot_registration else "Confirmed",
        lab_allotment=lab,
        mentor_name=mentor["name"],
        mentor_contact=mentor["contact"],
        project_title=project_label
    )
    db.add(new_team)
    db.commit()
    db.refresh(new_team)

    return {
        "success": True,
        "message": "Team registration successfully confirmed!",
        "registration_id": new_team.registration_id,
        "team_name": new_team.team_name,
        "lead_name": new_team.lead_name,
        "lead_email": new_team.lead_email,
        "lead_phone": new_team.lead_phone,
        "college": new_team.college,
        "track": new_team.track,
        "event": project_label,
        "members": processed_members,
        "lab_allotment": new_team.lab_allotment,
        "mentor_name": new_team.mentor_name,
        "mentor_contact": new_team.mentor_contact,
        "mode": new_team.mode,
        "guide": [
            "1. Save your Team ID: " + new_team.registration_id,
            "2. Connect to MCET High-Speed Hackathon Wi-Fi (SSID: HWI_MCET_5G, Pass: hackwithindia2026)",
            "3. Report to your allotted desk: " + new_team.lab_allotment,
            "4. Schedule initial 10-minute sync with your assigned mentor: " + new_team.mentor_name,
            "5. Fork the official Hack With India starter template from the Dashboard",
            "6. Keep track of the Live Sessions and join the Mid-Hack mini-games for bonus points!"
        ]
    }


# API: Spot Registration (Admin & On-Desk Walk-in)
@app.post("/api/spot-register")
def spot_register(data: models.TeamCreate, db: Session = Depends(get_db)):
    data.is_spot_registration = True
    data.mode = "Offline"
    return register_team(data=data, db=db)


# API: Get Allotment & Guide by Registration ID
@app.get("/api/allotment/{reg_id}")
def get_allotment(reg_id: str, db: Session = Depends(get_db)):
    team = db.query(models.TeamRegistration).filter(
        func.upper(models.TeamRegistration.registration_id) == reg_id.upper().strip()
    ).first()
    
    if not team:
        # Also check by team name
        team = db.query(models.TeamRegistration).filter(
            func.lower(models.TeamRegistration.team_name) == reg_id.lower().strip()
        ).first()

    if not team:
        raise HTTPException(status_code=404, detail="No registration found for ID / Team Name: " + reg_id)

    members_list = []
    try:
        members_list = json.loads(team.members)
    except Exception:
        members_list = [team.lead_name]

    return {
        "registration_id": team.registration_id,
        "team_name": team.team_name,
        "lead_name": team.lead_name,
        "lead_email": team.lead_email,
        "lead_phone": team.lead_phone,
        "college": team.college,
        "track": team.track,
        "mode": team.mode,
        "members": members_list,
        "is_spot_registration": team.is_spot_registration,
        "is_present": team.is_present,
        "status": team.status,
        "lab_allotment": team.lab_allotment,
        "mentor_name": team.mentor_name,
        "mentor_contact": team.mentor_contact,
        "project_title": team.project_title,
        "project_repo": team.project_repo,
        "scores": {
            "innovation": team.score_innovation,
            "technical": team.score_technical,
            "impact": team.score_impact,
            "ui_ux": team.score_ui_ux,
            "pitch": team.score_pitch,
            "total": team.total_score
        },
        "guide": [
            "Step 1: Check-in at Desk: " + team.lab_allotment,
            "Step 2: Connect to campus Wi-Fi SSID: HWI_MCET_5G (Pass: hackwithindia2026)",
            "Step 3: Meet Assigned Mentor: " + team.mentor_name + " (" + team.mentor_contact + ")",
            "Step 4: Push initial boilerplate to GitHub and submit repo in the Dashboard",
            "Step 5: Attend Mentoring Round 1 at 01:30 PM",
            "Step 6: Participate in the Gaming Quest at 04:30 PM for extra points",
            "Step 7: Final Pitch preparation adhering to the Winning Parameters matrix"
        ]
    }


# API: List All Teams
@app.get("/api/teams")
def list_teams(
    search: Optional[str] = None,
    track: Optional[str] = None,
    filter_present: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.TeamRegistration)

    if search:
        query = query.filter(
            models.TeamRegistration.team_name.ilike(f"%{search}%") |
            models.TeamRegistration.registration_id.ilike(f"%{search}%") |
            models.TeamRegistration.lead_name.ilike(f"%{search}%")
        )
    if track and track != "All":
        query = query.filter(models.TeamRegistration.track == track)

    if filter_present == "present":
        query = query.filter(models.TeamRegistration.is_present == True)
    elif filter_present == "absent":
        query = query.filter(models.TeamRegistration.is_present == False)
    elif filter_present == "spot":
        query = query.filter(models.TeamRegistration.is_spot_registration == True)

    teams = query.order_by(models.TeamRegistration.total_score.desc(), models.TeamRegistration.id.asc()).all()
    
    result = []
    for t in teams:
        members_list = []
        try:
            members_list = json.loads(t.members)
        except Exception:
            members_list = [t.lead_name]

        result.append({
            "id": t.id,
            "registration_id": t.registration_id,
            "team_name": t.team_name,
            "lead_name": t.lead_name,
            "lead_email": t.lead_email,
            "lead_phone": t.lead_phone,
            "college": t.college,
            "track": t.track,
            "mode": t.mode,
            "members": members_list,
            "is_spot_registration": t.is_spot_registration,
            "is_present": t.is_present,
            "status": t.status,
            "lab_allotment": t.lab_allotment,
            "mentor_name": t.mentor_name,
            "mentor_contact": t.mentor_contact,
            "project_title": t.project_title,
            "project_repo": t.project_repo,
            "total_score": t.total_score,
            "scores": {
                "innovation": t.score_innovation,
                "technical": t.score_technical,
                "impact": t.score_impact,
                "ui_ux": t.score_ui_ux,
                "pitch": t.score_pitch
            }
        })
    return result


# API: Attendance Toggle (Number of Presenties)
@app.post("/api/teams/{team_id}/attendance")
def toggle_attendance(team_id: int, payload: models.AttendanceToggle, db: Session = Depends(get_db)):
    team = db.query(models.TeamRegistration).filter(models.TeamRegistration.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    team.is_present = payload.is_present
    team.status = "Checked-In" if payload.is_present else "Confirmed"
    db.commit()
    
    present_count = db.query(models.TeamRegistration).filter(models.TeamRegistration.is_present == True).count()
    return {
        "success": True,
        "team_id": team.id,
        "is_present": team.is_present,
        "present_count": present_count,
        "status": team.status
    }


# API: Update Scores (Based on Winning Parameters)
@app.post("/api/teams/{team_id}/score")
def update_team_score(team_id: int, scores: models.ScoreUpdate, db: Session = Depends(get_db)):
    team = db.query(models.TeamRegistration).filter(models.TeamRegistration.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    team.score_innovation = scores.score_innovation
    team.score_technical = scores.score_technical
    team.score_impact = scores.score_impact
    team.score_ui_ux = scores.score_ui_ux
    team.score_pitch = scores.score_pitch
    team.total_score = round(
        scores.score_innovation + scores.score_technical + scores.score_impact + scores.score_ui_ux + scores.score_pitch,
        2
    )
    db.commit()

    return {
        "success": True,
        "team_id": team.id,
        "total_score": team.total_score,
        "scores": {
            "innovation": team.score_innovation,
            "technical": team.score_technical,
            "impact": team.score_impact,
            "ui_ux": team.score_ui_ux,
            "pitch": team.score_pitch
        }
    }


# API: Live Leaderboard
@app.get("/api/leaderboard")
def get_leaderboard(track: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.TeamRegistration)
    if track and track != "All":
        query = query.filter(models.TeamRegistration.track == track)
    
    teams = query.order_by(models.TeamRegistration.total_score.desc()).all()
    
    leaderboard = []
    for rank, t in enumerate(teams, start=1):
        leaderboard.append({
            "rank": rank,
            "id": t.id,
            "registration_id": t.registration_id,
            "team_name": t.team_name,
            "track": t.track,
            "college": t.college,
            "project_title": t.project_title or "Work In Progress",
            "scores": {
                "innovation": t.score_innovation,
                "technical": t.score_technical,
                "impact": t.score_impact,
                "ui_ux": t.score_ui_ux,
                "pitch": t.score_pitch
            },
            "total_score": t.total_score,
            "mode": t.mode,
            "is_present": t.is_present
        })
    return leaderboard


# API: Sessions (Offline, Hybrid, Leadership talks)
@app.get("/api/sessions")
def get_sessions(category: Optional[str] = None, mode: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.SessionItem).filter(models.SessionItem.is_published == True)
    if category and category != "All":
        query = query.filter(models.SessionItem.category == category)
    if mode and mode != "All":
        query = query.filter(models.SessionItem.mode.in_([mode, "Both"]))
    
    sessions = query.order_by(models.SessionItem.order_num.asc()).all()
    return sessions


# API: Events & Sessions Management (Supabase & Admin Panel Ready)
@app.get("/api/events")
def get_events(category: Optional[str] = None, mode: Optional[str] = None, db: Session = Depends(get_db)):
    return get_sessions(category=category, mode=mode, db=db)


@app.get("/api/events/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.SessionItem).filter(models.SessionItem.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.post("/api/events")
def create_event(payload: models.EventCreate, db: Session = Depends(get_db)):
    new_event = models.SessionItem(
        title=payload.title,
        speaker=payload.speaker or "Tech Lead / Industry Mentor",
        speaker_title=payload.speaker_title or "HWI Speaker",
        category=payload.category or "Workshop",
        time_slot=payload.time_slot,
        venue=payload.venue or "MCET Main Auditorium & Newton Lab",
        mode=payload.mode or "Offline",
        stream_url=payload.stream_url or "",
        description=payload.description or "",
        status=payload.status or "Upcoming",
        order_num=payload.order_num or 1,
        image_url=payload.image_url or "",
        registration_url=payload.registration_url or "",
        link_label=payload.link_label or "Register Now",
        secondary_link_url=payload.secondary_link_url or "",
        secondary_link_label=payload.secondary_link_label or "",
        badge_text=payload.badge_text or ""
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return {"status": "success", "message": "Event created successfully", "event": new_event}


@app.put("/api/events/{event_id}")
def update_event(event_id: int, payload: models.EventUpdate, db: Session = Depends(get_db)):
    event = db.query(models.SessionItem).filter(models.SessionItem.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    update_data = payload.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(event, field, val)
        
    db.commit()
    db.refresh(event)
    return {"status": "success", "message": "Event updated successfully", "event": event}


@app.delete("/api/events/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.SessionItem).filter(models.SessionItem.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return {"status": "success", "message": f"Event {event_id} deleted successfully"}


# API: Games Challenges
@app.get("/api/games")
def get_games(db: Session = Depends(get_db)):
    games = db.query(models.GameChallenge).all()
    results = []
    for g in games:
        results.append({
            "id": g.id,
            "title": g.title,
            "type": g.type,
            "question": g.question,
            "snippet": g.snippet,
            "options": json.loads(g.options) if g.options else [],
            "points": g.points,
            "explanation": g.explanation
        })
    return results


@app.post("/api/games/submit")
def submit_game_answer(
    game_id: int = Form(...),
    answer: str = Form(...),
    team_reg_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    game = db.query(models.GameChallenge).filter(models.GameChallenge.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Challenge not found")

    is_correct = (game.correct_answer.strip().lower() == answer.strip().lower())
    
    # Optional team point boost
    bonus_applied = False
    if is_correct and team_reg_id:
        team = db.query(models.TeamRegistration).filter(
            func.upper(models.TeamRegistration.registration_id) == team_reg_id.strip().upper()
        ).first()
        if team:
            # Grant a small innovation/technical bonus point (up to +1.0)
            bonus = min(1.0, round(game.points / 50.0, 1))
            team.score_technical = min(25.0, round(team.score_technical + bonus, 2))
            team.total_score = round(
                team.score_innovation + team.score_technical + team.score_impact + team.score_ui_ux + team.score_pitch,
                2
            )
            db.commit()
            bonus_applied = True

    return {
        "correct": is_correct,
        "points_earned": game.points if is_correct else 0,
        "correct_answer": game.correct_answer,
        "explanation": game.explanation,
        "bonus_applied": bonus_applied
    }


# API: Feedbacks (Students & Guests)
@app.get("/api/feedbacks")
def get_feedbacks(db: Session = Depends(get_db)):
    feedbacks = db.query(models.FeedbackItem).filter(models.FeedbackItem.is_visible == True).order_by(models.FeedbackItem.created_at.desc()).all()
    return feedbacks


@app.get("/api/feedback")
def get_feedback_alias(db: Session = Depends(get_db)):
    return get_feedbacks(db=db)


@app.post("/api/feedbacks")
def add_feedback(item: models.FeedbackCreate, db: Session = Depends(get_db)):
    # Sentiment calculation
    comment_lower = item.comment.lower()
    positive_keywords = ["great", "awesome", "vibecoding", "vibe", "love", "excellent", "super", "smooth", "phenomenal", "helpful"]
    if any(k in comment_lower for k in positive_keywords) or item.rating >= 4:
        sentiment = "Positive"
    elif item.rating <= 2:
        sentiment = "Suggestive"
    else:
        sentiment = "Insightful"

    new_feedback = models.FeedbackItem(
        author_name=item.author_name.strip(),
        role=item.role,
        rating=item.rating,
        category=item.category,
        comment=item.comment.strip(),
        sentiment=sentiment
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return {"success": True, "message": "Feedback submitted successfully!", "item": new_feedback}


@app.post("/api/feedback")
def add_feedback_alias(item: models.FeedbackCreate, db: Session = Depends(get_db)):
    return add_feedback(item=item, db=db)


# API: Summarize Feedbacks
@app.get("/api/feedbacks/summary")
def summarize_feedbacks(db: Session = Depends(get_db)):
    feedbacks = db.query(models.FeedbackItem).all()
    total = len(feedbacks)
    if total == 0:
        return {
            "total_reviews": 0,
            "average_rating": 0.0,
            "sentiment_breakdown": {"Positive": 0, "Insightful": 0, "Suggestive": 0},
            "top_highlights": [],
            "action_items": [],
            "executive_summary": "No attendee feedback has been recorded yet. Share your experience using the feedback form."
        }

    ratings = [f.rating for f in feedbacks]
    avg_rating = round(sum(ratings) / total, 2)
    
    pos_count = sum(1 for f in feedbacks if f.sentiment == "Positive" or f.rating >= 4)
    ins_count = sum(1 for f in feedbacks if f.sentiment == "Insightful")
    sug_count = total - pos_count - ins_count
    if sug_count < 0:
        sug_count = 0

    executive_summary = (
        f"Based on {total} authentic review{'s' if total != 1 else ''} recorded for Hack with India MCET Chapter, "
        f"the current satisfaction index is {avg_rating}/5.0 across recorded attendee submissions."
    )

    # Use actual feedback remarks rather than fabricated quotes
    recent_feedback = [f.comment for f in feedbacks[-4:]]

    return {
        "total_reviews": total,
        "average_rating": avg_rating,
        "sentiment_breakdown": {
            "Positive": round((pos_count / total) * 100),
            "Insightful": round((ins_count / total) * 100),
            "Suggestive": round((sug_count / total) * 100) if total > (pos_count + ins_count) else 0
        },
        "top_highlights": recent_feedback,
        "action_items": ["Monitor active lab desks and mentor coordination", "Collect post-event feedback"],
        "executive_summary": executive_summary
    }


# API: Blog of HWI (Pics, Notifications, Banners)
@app.get("/api/blog")
def get_blog(db: Session = Depends(get_db)):
    blogs = db.query(models.BlogItem).order_by(models.BlogItem.pinned.desc(), models.BlogItem.created_at.desc()).all()
    return blogs


@app.post("/api/blog")
def add_blog(item: models.BlogCreate, db: Session = Depends(get_db)):
    new_blog = models.BlogItem(
        title=item.title.strip(),
        category=item.category,
        image_url=item.image_url or "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=1200&q=80",
        author=item.author or "HWI MCET Organizing Cell",
        summary=item.summary.strip(),
        content=item.content.strip(),
        pinned=bool(item.pinned)
    )
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return {"success": True, "message": "Blog / Banner published to HWI stream!", "item": new_blog}


# Mount Private Admin Dashboard Router
from admin_routes import admin_router
app.include_router(admin_router)
