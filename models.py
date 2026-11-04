"""
Database models and Pydantic schemas for Hack With India @ MCET Campus
Includes Public Portal models and Administrative Security & Management models.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, Text, DateTime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any, Union
from database import Base

# ==========================================
# SQLAlchemy Models
# ==========================================

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)


class AdminAuditLog(Base):
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_username = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(Text, default="")
    ip_address = Column(String(100), default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class TeamMemberItem(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    role = Column(String(120), nullable=False)
    bio = Column(Text, default="")
    photo_url = Column(Text, default="")
    github_url = Column(String(255), default="")
    linkedin_url = Column(String(255), default="")
    twitter_url = Column(String(255), default="")
    order_num = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SiteSettings(Base):
    __tablename__ = "site_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(Text, default="")
    description = Column(String(255), default="")
    updated_at = Column(DateTime, default=datetime.utcnow)


class TeamRegistration(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(String(50), unique=True, index=True)
    team_name = Column(String(100), nullable=False)
    lead_name = Column(String(100), nullable=False)
    lead_email = Column(String(120), nullable=False)
    lead_phone = Column(String(20), nullable=False)
    college = Column(String(150), default="MCET Campus")
    track = Column(String(80), nullable=False)
    members = Column(Text, default="[]")  # JSON encoded list of member names
    mode = Column(String(30), default="Offline")  # Offline / Hybrid
    is_spot_registration = Column(Boolean, default=False)
    is_present = Column(Boolean, default=False)  # Check-in attendance
    status = Column(String(30), default="Confirmed")  # Confirmed, Checked-In, In-Review, Rejected
    
    # Event linkage
    event_id = Column(Integer, nullable=True)
    event_title = Column(String(150), default="")

    # Allotment Information
    lab_allotment = Column(String(120), default="Pending Allotment")
    mentor_name = Column(String(100), default="To Be Assigned")
    mentor_contact = Column(String(100), default="")
    
    # Project & Submission
    project_title = Column(String(150), default="")
    project_repo = Column(String(255), default="")
    
    # Winning Parameter Scores
    score_innovation = Column(Float, default=0.0)  # max 25
    score_technical = Column(Float, default=0.0)   # max 25
    score_impact = Column(Float, default=0.0)      # max 20
    score_ui_ux = Column(Float, default=0.0)       # max 15
    score_pitch = Column(Float, default=0.0)       # max 15
    total_score = Column(Float, default=0.0)       # max 100
    
    created_at = Column(DateTime, default=datetime.utcnow)


class SessionItem(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    speaker = Column(String(100), nullable=False)
    speaker_title = Column(String(150), default="Tech Lead / Industry Mentor")
    category = Column(String(50), default="Workshop")  # Hackathon, Workshop, Keynote, Mentoring, Panel
    time_slot = Column(String(80), nullable=False)
    venue = Column(String(120), default="MCET Main Auditorium & Newton Lab")
    mode = Column(String(40), default="Offline")  # Offline, Hybrid, Virtual
    stream_url = Column(String(255), default="")
    description = Column(Text, default="")
    status = Column(String(30), default="Upcoming")  # Upcoming, Live Now, Completed
    order_num = Column(Integer, default=1)
    image_url = Column(Text, default="")
    registration_url = Column(Text, default="")
    link_label = Column(String(100), default="Register Now")
    secondary_link_url = Column(Text, default="")
    secondary_link_label = Column(String(100), default="")
    badge_text = Column(String(80), default="")
    
    # Admin Controls
    is_published = Column(Boolean, default=True)
    registration_open = Column(Boolean, default=True)
    capacity = Column(Integer, default=100)
    team_size_min = Column(Integer, default=1)
    team_size_max = Column(Integer, default=4)
    reg_start_date = Column(String(80), default="")
    reg_end_date = Column(String(80), default="")


class FeedbackItem(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    author_name = Column(String(100), nullable=False)
    role = Column(String(50), default="Student Participant")
    rating = Column(Integer, default=5)
    category = Column(String(60), default="Overall Hackathon Vibe")
    comment = Column(Text, nullable=False)
    sentiment = Column(String(30), default="Positive")  # Positive, Neutral, Insightful
    is_visible = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class BlogItem(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(60), default="Announcement")  # Announcement, Photo Highlights, Banner / Notice, Leaderboard
    image_url = Column(String(300), default="")
    author = Column(String(100), default="HWI MCET Team")
    summary = Column(Text, default="")
    content = Column(Text, default="")
    pinned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class GameChallenge(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    type = Column(String(50), default="speed_debug")  # speed_debug, cyber_trivia, typing_dash
    question = Column(Text, nullable=False)
    snippet = Column(Text, default="")
    options = Column(Text, default="[]")  # JSON string
    correct_answer = Column(String(150), nullable=False)
    explanation = Column(Text, default="")
    points = Column(Integer, default=50)


# ==========================================
# Pydantic Schemas for Requests
# ==========================================

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminPasswordChange(BaseModel):
    current_password: str
    new_password: str

class AdminCredentialUpdate(BaseModel):
    current_password: str
    new_username: Optional[str] = None
    new_password: Optional[str] = None

class TeamMemberCreate(BaseModel):
    name: str
    role: str
    bio: Optional[str] = ""
    photo_url: Optional[str] = ""
    github_url: Optional[str] = ""
    linkedin_url: Optional[str] = ""
    twitter_url: Optional[str] = ""
    order_num: Optional[int] = 1
    is_active: Optional[bool] = True

class TeamMemberUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    order_num: Optional[int] = None
    is_active: Optional[bool] = None

class SiteSettingUpdate(BaseModel):
    key: str
    value: str
    description: Optional[str] = ""

class TeamCreate(BaseModel):
    team_name: str
    lead_name: str
    lead_email: str
    lead_phone: str
    college: Optional[str] = "MCET Campus"
    track: str
    members: Optional[List[Any]] = []
    mode: Optional[str] = "Offline"
    is_spot_registration: Optional[bool] = False
    event_id: Optional[int] = None
    event_title: Optional[str] = None

class RegistrationStatusUpdate(BaseModel):
    status: str
    lab_allotment: Optional[str] = None
    mentor_name: Optional[str] = None
    mentor_contact: Optional[str] = None
    is_present: Optional[bool] = None

class ScoreUpdate(BaseModel):
    score_innovation: float = Field(..., ge=0, le=25)
    score_technical: float = Field(..., ge=0, le=25)
    score_impact: float = Field(..., ge=0, le=20)
    score_ui_ux: float = Field(..., ge=0, le=15)
    score_pitch: float = Field(..., ge=0, le=15)

class FeedbackCreate(BaseModel):
    author_name: str
    role: str
    rating: int = Field(..., ge=1, le=5)
    category: str
    comment: str

class BlogCreate(BaseModel):
    title: str
    category: str
    image_url: Optional[str] = ""
    author: Optional[str] = "HWI MCET Organizing Committee"
    summary: str
    content: str
    pinned: Optional[bool] = False

class BlogUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    author: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    pinned: Optional[bool] = None

class AttendanceToggle(BaseModel):
    is_present: bool

class EventCreate(BaseModel):
    title: str
    speaker: Optional[str] = "Tech Lead / Industry Mentor"
    speaker_title: Optional[str] = "HWI Speaker"
    category: Optional[str] = "Workshop"
    time_slot: str
    venue: Optional[str] = "MCET Main Auditorium & Newton Lab"
    mode: Optional[str] = "Offline"
    stream_url: Optional[str] = ""
    description: Optional[str] = ""
    status: Optional[str] = "Upcoming"
    order_num: Optional[int] = 1
    image_url: Optional[str] = ""
    registration_url: Optional[str] = ""
    link_label: Optional[str] = "Register Now"
    secondary_link_url: Optional[str] = ""
    secondary_link_label: Optional[str] = ""
    badge_text: Optional[str] = ""
    is_published: Optional[bool] = True
    registration_open: Optional[bool] = True
    capacity: Optional[int] = 100
    team_size_min: Optional[int] = 1
    team_size_max: Optional[int] = 4
    reg_start_date: Optional[str] = ""
    reg_end_date: Optional[str] = ""

class EventUpdate(BaseModel):
    title: Optional[str] = None
    speaker: Optional[str] = None
    speaker_title: Optional[str] = None
    category: Optional[str] = None
    time_slot: Optional[str] = None
    venue: Optional[str] = None
    mode: Optional[str] = None
    stream_url: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    order_num: Optional[int] = None
    image_url: Optional[str] = None
    registration_url: Optional[str] = None
    link_label: Optional[str] = None
    secondary_link_url: Optional[str] = None
    secondary_link_label: Optional[str] = None
    badge_text: Optional[str] = None
    is_published: Optional[bool] = None
    registration_open: Optional[bool] = None
    capacity: Optional[int] = None
    team_size_min: Optional[int] = None
    team_size_max: Optional[int] = None
    reg_start_date: Optional[str] = None
    reg_end_date: Optional[str] = None

class GameChallengeCreate(BaseModel):
    title: str
    type: Optional[str] = "speed_debug"
    question: str
    snippet: Optional[str] = ""
    options: Optional[str] = "[]"
    correct_answer: str
    explanation: Optional[str] = ""
    points: Optional[int] = 50

class GameChallengeUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    question: Optional[str] = None
    snippet: Optional[str] = None
    options: Optional[str] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    points: Optional[int] = None
