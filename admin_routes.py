"""
Admin Dashboard & API Routes for Hack With India x MCET Chapter
Provides 10 isolated administrative interfaces, protected endpoints, and audit logging.
Strictly Zero Seeded Data constraint honored.
"""
import csv
import io
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func

import models
from database import get_db
import admin_auth

import os

admin_router = APIRouter()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# ==========================================
# Helper: Extract Participant Count Accurately
# ==========================================
def calculate_participant_count(teams: List[models.TeamRegistration]) -> int:
    """Calculates total builders (1 leader + roster members per registered team)."""
    total = 0
    for t in teams:
        total += 1  # Team leader
        try:
            members = json.loads(t.members or "[]")
            if isinstance(members, list):
                total += len(members)
        except Exception:
            pass
    return total

# ==========================================
# 1. Authentication Endpoints
# ==========================================

@admin_router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request, db: Session = Depends(get_db)):
    """Admin Login Portal. Redirects to /admin if already authenticated."""
    token = request.cookies.get("hwi_admin_token")
    if token and admin_auth.decode_admin_token(token):
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(request=request, name="admin/login.html", context={})


@admin_router.post("/api/admin/login")
async def api_admin_login(request: Request, data: models.AdminLoginRequest, db: Session = Depends(get_db)):
    """Validates administrator credentials, enforces IP rate limits, and issues JWT cookie."""
    client_ip = admin_auth.get_client_ip(request)

    # Rate limiting check
    is_blocked, remaining = admin_auth.check_rate_limit(client_ip)
    if is_blocked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Too many failed attempts. Try again in {remaining} seconds."
        )

    # Query admin record
    clean_username = data.username.strip()
    admin = db.query(models.AdminUser).filter(
        func.lower(models.AdminUser.username) == clean_username.lower(),
        models.AdminUser.is_active == True
    ).first()

    if not admin or not admin_auth.verify_password(data.password, admin.password_hash):
        admin_auth.record_failed_attempt(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid administrator username or password."
        )

    # Success: reset rate limit & update last_login
    admin_auth.reset_rate_limit(client_ip)
    admin.last_login = datetime.utcnow()
    db.commit()

    # Log action
    admin_auth.log_admin_action(
        db=db,
        username=admin.username,
        action="ADMIN_LOGIN",
        details="Administrator successfully logged into control console.",
        ip=client_ip
    )

    # Generate token & set HttpOnly cookie
    token = admin_auth.create_admin_token(admin.username)
    response = Response(
        content=json.dumps({"status": "success", "username": admin.username}),
        media_type="application/json"
    )
    response.set_cookie(
        key="hwi_admin_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=8 * 3600,
        path="/"
    )
    return response


@admin_router.get("/admin/logout")
@admin_router.post("/api/admin/logout")
async def admin_logout(request: Request, db: Session = Depends(get_db)):
    """Terminates admin session and clears auth cookie."""
    token = request.cookies.get("hwi_admin_token")
    if token:
        user = admin_auth.decode_admin_token(token)
        if user:
            client_ip = admin_auth.get_client_ip(request)
            admin_auth.log_admin_action(db, user, "ADMIN_LOGOUT", "Session terminated by user.", client_ip)

    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="hwi_admin_token", path="/")
    return response


# ==========================================
# 2. Admin Dashboard Overview
# ==========================================

@admin_router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """Admin Overview Dashboard with actual database KPIs and zero mock data."""
    admin = admin_auth.get_current_admin(request, db)

    # Real database metrics
    all_teams = db.query(models.TeamRegistration).all()
    events_count = db.query(models.SessionItem).count()
    published_events_count = db.query(models.SessionItem).filter(models.SessionItem.is_published == True).count()
    registrations_count = len(all_teams)
    participants_count = calculate_participant_count(all_teams)
    feedbacks_count = db.query(models.FeedbackItem).count()

    recent_registrations = db.query(models.TeamRegistration).order_by(models.TeamRegistration.created_at.desc()).limit(5).all()
    audit_logs = db.query(models.AdminAuditLog).order_by(models.AdminAuditLog.created_at.desc()).limit(15).all()

    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "admin_user": admin,
            "active_page": "dashboard",
            "stats": {
                "events_count": events_count,
                "published_events_count": published_events_count,
                "registrations_count": registrations_count,
                "participants_count": participants_count,
                "feedbacks_count": feedbacks_count
            },
            "recent_registrations": recent_registrations,
            "audit_logs": audit_logs
        }
    )


# ==========================================
# 3. Events Management
# ==========================================

@admin_router.get("/admin/events", response_class=HTMLResponse)
async def admin_events_page(request: Request, db: Session = Depends(get_db)):
    """Admin Events & Sessions Management Interface."""
    admin = admin_auth.get_current_admin(request, db)
    events = db.query(models.SessionItem).order_by(models.SessionItem.order_num.asc(), models.SessionItem.id.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="admin/events.html",
        context={
            "admin_user": admin,
            "active_page": "events",
            "events": events
        }
    )


@admin_router.get("/api/admin/events")
async def api_admin_get_events(request: Request, db: Session = Depends(get_db)):
    """Fetch all events including draft states."""
    admin_auth.get_current_admin(request, db)
    return db.query(models.SessionItem).order_by(models.SessionItem.order_num.asc()).all()


@admin_router.get("/api/admin/events/{event_id}")
async def api_admin_get_single_event(event_id: int, request: Request, db: Session = Depends(get_db)):
    """Fetch specific event details."""
    admin_auth.get_current_admin(request, db)
    ev = db.query(models.SessionItem).filter(models.SessionItem.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found.")
    return ev


@admin_router.post("/api/admin/events")
async def api_admin_create_event(data: models.EventCreate, request: Request, db: Session = Depends(get_db)):
    """Create a new event."""
    admin = admin_auth.get_current_admin(request, db)
    new_event = models.SessionItem(
        title=data.title.strip(),
        speaker=data.speaker or "Organizing Core",
        speaker_title=data.speaker_title or "MCET Chapter Lead",
        category=data.category or "Workshop",
        time_slot=data.time_slot.strip(),
        venue=data.venue or "MCET Newton Lab & Auditorium",
        mode=data.mode or "Offline",
        stream_url=data.stream_url or "",
        description=data.description or "",
        status=data.status or "Upcoming",
        order_num=data.order_num or 1,
        image_url=data.image_url or "",
        registration_url=data.registration_url or "",
        link_label=data.link_label or "Register Now",
        badge_text=data.badge_text or "",
        is_published=bool(data.is_published),
        registration_open=bool(data.registration_open),
        capacity=data.capacity or 100,
        team_size_min=data.team_size_min or 1,
        team_size_max=data.team_size_max or 4,
        reg_start_date=data.reg_start_date or "",
        reg_end_date=data.reg_end_date or ""
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    admin_auth.log_admin_action(
        db, admin.username, "EVENT_CREATED",
        f"Created event '{new_event.title}' (ID: {new_event.id}, Published: {new_event.is_published})",
        admin_auth.get_client_ip(request)
    )
    return {
        "status": "success",
        "event": {
            "id": new_event.id,
            "title": new_event.title,
            "category": new_event.category,
            "time_slot": new_event.time_slot,
            "is_published": new_event.is_published
        }
    }


@admin_router.put("/api/admin/events/{event_id}")
async def api_admin_update_event(event_id: int, data: models.EventUpdate, request: Request, db: Session = Depends(get_db)):
    """Update event properties."""
    admin = admin_auth.get_current_admin(request, db)
    ev = db.query(models.SessionItem).filter(models.SessionItem.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found.")

    update_dict = data.dict(exclude_unset=True)
    for k, v in update_dict.items():
        if v is not None:
            setattr(ev, k, v)

    db.commit()
    db.refresh(ev)

    admin_auth.log_admin_action(
        db, admin.username, "EVENT_UPDATED",
        f"Updated event '{ev.title}' (ID: {ev.id})",
        admin_auth.get_client_ip(request)
    )
    return {"status": "success", "event": ev}


@admin_router.post("/api/admin/events/{event_id}/toggle-publish")
async def api_admin_toggle_publish(event_id: int, request: Request, db: Session = Depends(get_db)):
    """Toggle public visibility of an event."""
    admin = admin_auth.get_current_admin(request, db)
    ev = db.query(models.SessionItem).filter(models.SessionItem.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found.")

    try:
        body = await request.json()
        ev.is_published = bool(body.get("is_published", not ev.is_published))
    except Exception:
        ev.is_published = not ev.is_published

    db.commit()
    action = "EVENT_PUBLISHED" if ev.is_published else "EVENT_UNPUBLISHED"
    admin_auth.log_admin_action(
        db, admin.username, action,
        f"Event '{ev.title}' is now {'Published' if ev.is_published else 'Unpublished'}.",
        admin_auth.get_client_ip(request)
    )
    return {"status": "success", "is_published": ev.is_published}


@admin_router.delete("/api/admin/events/{event_id}")
async def api_admin_delete_event(event_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete an event."""
    admin = admin_auth.get_current_admin(request, db)
    ev = db.query(models.SessionItem).filter(models.SessionItem.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found.")

    title = ev.title
    db.delete(ev)
    db.commit()

    admin_auth.log_admin_action(
        db, admin.username, "EVENT_DELETED",
        f"Deleted event '{title}' (ID: {event_id})",
        admin_auth.get_client_ip(request)
    )
    return {"status": "success", "message": f"Event '{title}' deleted."}


# ==========================================
# 4. Registration Management & CSV Export
# ==========================================

@admin_router.get("/admin/registrations", response_class=HTMLResponse)
async def admin_registrations_page(request: Request, db: Session = Depends(get_db)):
    """Admin Registrations Management View."""
    admin = admin_auth.get_current_admin(request, db)
    registrations = db.query(models.TeamRegistration).order_by(models.TeamRegistration.created_at.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="admin/registrations.html",
        context={
            "admin_user": admin,
            "active_page": "registrations",
            "registrations": registrations
        }
    )


@admin_router.get("/api/admin/registrations")
async def api_admin_get_registrations(request: Request, db: Session = Depends(get_db)):
    """List all registrations."""
    admin_auth.get_current_admin(request, db)
    return db.query(models.TeamRegistration).order_by(models.TeamRegistration.created_at.desc()).all()


@admin_router.put("/api/admin/registrations/{reg_id}")
async def api_admin_update_registration(reg_id: int, data: models.RegistrationStatusUpdate, request: Request, db: Session = Depends(get_db)):
    """Update registration status, lab desk allotment, or mentor."""
    admin = admin_auth.get_current_admin(request, db)
    reg = db.query(models.TeamRegistration).filter(models.TeamRegistration.id == reg_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found.")

    reg.status = data.status
    if data.lab_allotment is not None:
        reg.lab_allotment = data.lab_allotment
    if data.mentor_name is not None:
        reg.mentor_name = data.mentor_name
    if data.mentor_contact is not None:
        reg.mentor_contact = data.mentor_contact
    if data.is_present is not None:
        reg.is_present = data.is_present

    db.commit()
    db.refresh(reg)

    admin_auth.log_admin_action(
        db, admin.username, "REGISTRATION_UPDATED",
        f"Updated registration {reg.registration_id} (Team: '{reg.team_name}', Status: '{reg.status}', Lab: '{reg.lab_allotment}')",
        admin_auth.get_client_ip(request)
    )
    return {"status": "success", "registration": reg}


@admin_router.delete("/api/admin/registrations/{reg_id}")
async def api_admin_delete_registration(reg_id: int, request: Request, db: Session = Depends(get_db)):
    """Remove a registration entry."""
    admin = admin_auth.get_current_admin(request, db)
    reg = db.query(models.TeamRegistration).filter(models.TeamRegistration.id == reg_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found.")

    team_name = reg.team_name
    code = reg.registration_id
    db.delete(reg)
    db.commit()

    admin_auth.log_admin_action(
        db, admin.username, "REGISTRATION_DELETED",
        f"Deleted registration {code} for team '{team_name}'",
        admin_auth.get_client_ip(request)
    )
    return {"status": "success", "message": f"Registration {code} deleted."}


@admin_router.get("/api/admin/registrations/export")
async def api_admin_export_registrations_csv(request: Request, db: Session = Depends(get_db)):
    """Export authorized registration records as CSV."""
    admin_auth.get_current_admin(request, db)
    registrations = db.query(models.TeamRegistration).order_by(models.TeamRegistration.created_at.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header Row
    writer.writerow([
        "Registration ID",
        "Team Name",
        "Leader Name",
        "Leader Email",
        "Leader Phone",
        "College",
        "Track",
        "Mode",
        "Roster Members",
        "Total Count",
        "Lab Allotment",
        "Mentor Assigned",
        "Attendance Checked In",
        "Status",
        "Registration Date"
    ])

    for r in registrations:
        members_list = []
        try:
            raw = json.loads(r.members or "[]")
            for m in raw:
                if isinstance(m, dict):
                    members_list.append(m.get("name", ""))
                elif isinstance(m, str):
                    members_list.append(m)
        except Exception:
            pass
        members_str = "; ".join(members_list) if members_list else "None"
        total_builders = 1 + len(members_list)

        writer.writerow([
            r.registration_id,
            r.team_name,
            r.lead_name,
            r.lead_email,
            r.lead_phone,
            r.college,
            r.track,
            r.mode,
            members_str,
            total_builders,
            r.lab_allotment,
            r.mentor_name,
            "Yes" if r.is_present else "No",
            r.status,
            r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else ""
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=hwi_mcet_registrations_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )


# ==========================================
# 5. Announcements Management
# ==========================================

@admin_router.get("/admin/announcements", response_class=HTMLResponse)
async def admin_announcements_page(request: Request, db: Session = Depends(get_db)):
    """Admin Announcements Management."""
    admin = admin_auth.get_current_admin(request, db)
    announcements = db.query(models.BlogItem).order_by(models.BlogItem.pinned.desc(), models.BlogItem.created_at.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="admin/announcements.html",
        context={
            "admin_user": admin,
            "active_page": "announcements",
            "announcements": announcements
        }
    )


@admin_router.get("/api/admin/announcements/{ann_id}")
async def api_admin_get_announcement(ann_id: int, request: Request, db: Session = Depends(get_db)):
    """Get single announcement details."""
    admin_auth.get_current_admin(request, db)
    ann = db.query(models.BlogItem).filter(models.BlogItem.id == ann_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found.")
    return ann


@admin_router.post("/api/admin/announcements")
async def api_admin_create_announcement(data: models.BlogCreate, request: Request, db: Session = Depends(get_db)):
    """Publish an announcement."""
    admin = admin_auth.get_current_admin(request, db)
    ann = models.BlogItem(
        title=data.title.strip(),
        category=data.category,
        image_url=data.image_url.strip() if data.image_url else "",
        author=data.author or "HWI MCET Organizing Cell",
        summary=data.summary.strip(),
        content=data.content.strip(),
        pinned=bool(data.pinned)
    )
    db.add(ann)
    db.commit()
    db.refresh(ann)

    admin_auth.log_admin_action(
        db, admin.username, "ANNOUNCEMENT_CREATED",
        f"Published announcement '{ann.title}' (Pinned: {ann.pinned})",
        admin_auth.get_client_ip(request)
    )
    return {"status": "success", "item": {"id": ann.id, "title": ann.title}}


@admin_router.put("/api/admin/announcements/{ann_id}")
async def api_admin_update_announcement(ann_id: int, data: models.BlogUpdate, request: Request, db: Session = Depends(get_db)):
    """Update an announcement."""
    admin = admin_auth.get_current_admin(request, db)
    ann = db.query(models.BlogItem).filter(models.BlogItem.id == ann_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found.")

    update_dict = data.dict(exclude_unset=True)
    for k, v in update_dict.items():
        if v is not None:
            setattr(ann, k, v)

    db.commit()
    db.refresh(ann)

    admin_auth.log_admin_action(
        db, admin.username, "ANNOUNCEMENT_UPDATED",
        f"Updated announcement '{ann.title}'",
        admin_auth.get_client_ip(request)
    )
    return {"status": "success", "item": {"id": ann.id, "title": ann.title}}


@admin_router.delete("/api/admin/announcements/{ann_id}")
async def api_admin_delete_announcement(ann_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete an announcement."""
    admin = admin_auth.get_current_admin(request, db)
    ann = db.query(models.BlogItem).filter(models.BlogItem.id == ann_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found.")

    title = ann.title
    db.delete(ann)
    db.commit()

    admin_auth.log_admin_action(
        db, admin.username, "ANNOUNCEMENT_DELETED",
        f"Deleted announcement '{title}'",
        admin_auth.get_client_ip(request)
    )
    return {"status": "success", "message": f"Announcement '{title}' deleted."}


# ==========================================
# 6. Team Council Management
# ==========================================

@admin_router.get("/admin/team", response_class=HTMLResponse)
async def admin_team_page(request: Request, db: Session = Depends(get_db)):
    """Admin Team Council Management."""
    admin = admin_auth.get_current_admin(request, db)
    team_members = db.query(models.TeamMemberItem).order_by(models.TeamMemberItem.order_num.asc()).all()
    return templates.TemplateResponse(
        request=request,
        name="admin/team.html",
        context={
            "admin_user": admin,
            "active_page": "team",
            "team_members": team_members
        }
    )


@admin_router.get("/api/admin/team/{member_id}")
async def api_admin_get_member(member_id: int, request: Request, db: Session = Depends(get_db)):
    """Get single council profile."""
    admin_auth.get_current_admin(request, db)
    mem = db.query(models.TeamMemberItem).filter(models.TeamMemberItem.id == member_id).first()
    if not mem:
        raise HTTPException(status_code=404, detail="Member profile not found.")
    return mem


@admin_router.post("/api/admin/team")
async def api_admin_create_member(data: models.TeamMemberCreate, request: Request, db: Session = Depends(get_db)):
    """Add council member."""
    admin = admin_auth.get_current_admin(request, db)
    mem = models.TeamMemberItem(
        name=data.name.strip(),
        role=data.role.strip(),
        bio=data.bio or "",
        photo_url=data.photo_url or "",
        github_url=data.github_url or "",
        linkedin_url=data.linkedin_url or "",
        twitter_url=data.twitter_url or "",
        order_num=data.order_num or 1,
        is_active=bool(data.is_active)
    )
    db.add(mem)
    db.commit()
    db.refresh(mem)

    admin_auth.log_admin_action(
        db, admin.username, "TEAM_MEMBER_ADDED",
        f"Added council profile '{mem.name}' ({mem.role})",
        admin_auth.get_client_ip(request)
    )
    return {"status": "success", "member": {"id": mem.id, "name": mem.name}}


@admin_router.put("/api/admin/team/{member_id}")
async def api_admin_update_member(member_id: int, data: models.TeamMemberUpdate, request: Request, db: Session = Depends(get_db)):
    """Update council profile."""
    admin = admin_auth.get_current_admin(request, db)
    mem = db.query(models.TeamMemberItem).filter(models.TeamMemberItem.id == member_id).first()
    if not mem:
        raise HTTPException(status_code=404, detail="Member profile not found.")

    update_dict = data.dict(exclude_unset=True)
    for k, v in update_dict.items():
        if v is not None:
            setattr(mem, k, v)

    db.commit()
    db.refresh(mem)

    admin_auth.log_admin_action(
        db, admin.username, "TEAM_MEMBER_UPDATED",
        f"Updated council profile '{mem.name}'",
        admin_auth.get_client_ip(request)
    )
    return {"status": "success", "member": {"id": mem.id, "name": mem.name}}


@admin_router.delete("/api/admin/team/{member_id}")
async def api_admin_delete_member(member_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete council profile."""
    admin = admin_auth.get_current_admin(request, db)
    mem = db.query(models.TeamMemberItem).filter(models.TeamMemberItem.id == member_id).first()
    if not mem:
        raise HTTPException(status_code=404, detail="Member profile not found.")

    name = mem.name
    db.delete(mem)
    db.commit()

    admin_auth.log_admin_action(
        db, admin.username, "TEAM_MEMBER_DELETED",
        f"Removed council profile '{name}'",
        admin_auth.get_client_ip(request)
    )
    return {"status": "success", "message": f"Member '{name}' removed."}


# ==========================================
# 7. Schedule Management
# ==========================================

@admin_router.get("/admin/schedule", response_class=HTMLResponse)
async def admin_schedule_page(request: Request, db: Session = Depends(get_db)):
    """Admin Schedule Management."""
    admin = admin_auth.get_current_admin(request, db)
    sessions = db.query(models.SessionItem).order_by(models.SessionItem.order_num.asc()).all()
    return templates.TemplateResponse(
        request=request,
        name="admin/schedule.html",
        context={
            "admin_user": admin,
            "active_page": "schedule",
            "sessions": sessions
        }
    )


# ==========================================
# 8. Feedback Moderation
# ==========================================

@admin_router.get("/admin/feedback", response_class=HTMLResponse)
async def admin_feedback_page(request: Request, db: Session = Depends(get_db)):
    """Admin Feedback Moderation."""
    admin = admin_auth.get_current_admin(request, db)
    feedbacks = db.query(models.FeedbackItem).order_by(models.FeedbackItem.created_at.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="admin/feedback.html",
        context={
            "admin_user": admin,
            "active_page": "feedback",
            "feedbacks": feedbacks
        }
    )


@admin_router.post("/api/admin/feedback/{fb_id}/visibility")
async def api_admin_toggle_feedback_visibility(fb_id: int, request: Request, db: Session = Depends(get_db)):
    """Moderate feedback visibility."""
    admin = admin_auth.get_current_admin(request, db)
    fb = db.query(models.FeedbackItem).filter(models.FeedbackItem.id == fb_id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found.")

    try:
        body = await request.json()
        fb.is_visible = bool(body.get("is_visible", not fb.is_visible))
    except Exception:
        fb.is_visible = not fb.is_visible

    db.commit()
    admin_auth.log_admin_action(
        db, admin.username, "FEEDBACK_MODERATED",
        f"Feedback ID {fb.id} visibility toggled to {fb.is_visible}",
        admin_auth.get_client_ip(request)
    )
    return {"status": "success", "is_visible": fb.is_visible}


@admin_router.delete("/api/admin/feedback/{fb_id}")
async def api_admin_delete_feedback(fb_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete a feedback entry."""
    admin = admin_auth.get_current_admin(request, db)
    fb = db.query(models.FeedbackItem).filter(models.FeedbackItem.id == fb_id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found.")

    db.delete(fb)
    db.commit()

    admin_auth.log_admin_action(
        db, admin.username, "FEEDBACK_DELETED",
        f"Deleted feedback ID {fb_id} from '{fb.author_name}'",
        admin_auth.get_client_ip(request)
    )
    return {"status": "success", "message": f"Feedback {fb_id} deleted."}


# ==========================================
# 9. Gaming Arena Management
# ==========================================

@admin_router.get("/admin/games", response_class=HTMLResponse)
async def admin_games_page(request: Request, db: Session = Depends(get_db)):
    """Admin Games & Arena Challenges."""
    admin = admin_auth.get_current_admin(request, db)
    games = db.query(models.GameChallenge).all()
    return templates.TemplateResponse(
        request=request,
        name="admin/games.html",
        context={
            "admin_user": admin,
            "active_page": "games",
            "games": games
        }
    )


@admin_router.get("/api/admin/games/{game_id}")
async def api_admin_get_game(game_id: int, request: Request, db: Session = Depends(get_db)):
    """Get single challenge."""
    admin_auth.get_current_admin(request, db)
    g = db.query(models.GameChallenge).filter(models.GameChallenge.id == game_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Challenge not found.")
    return g


@admin_router.post("/api/admin/games")
async def api_admin_create_game(data: models.GameChallengeCreate, request: Request, db: Session = Depends(get_db)):
    """Create arena challenge."""
    admin = admin_auth.get_current_admin(request, db)
    game = models.GameChallenge(
        title=data.title.strip(),
        type=data.type or "speed_debug",
        question=data.question.strip(),
        snippet=data.snippet or "",
        options=data.options or "[]",
        correct_answer=data.correct_answer.strip(),
        explanation=data.explanation or "",
        points=data.points or 50
    )
    db.add(game)
    db.commit()
    db.refresh(game)

    admin_auth.log_admin_action(
        db, admin.username, "GAME_CREATED",
        f"Created arena challenge '{game.title}' ({game.points} pts)",
        admin_auth.get_client_ip(request)
    )
    return {"status": "success", "game": {"id": game.id, "title": game.title}}


@admin_router.put("/api/admin/games/{game_id}")
async def api_admin_update_game(game_id: int, data: models.GameChallengeUpdate, request: Request, db: Session = Depends(get_db)):
    """Update arena challenge."""
    admin = admin_auth.get_current_admin(request, db)
    g = db.query(models.GameChallenge).filter(models.GameChallenge.id == game_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Challenge not found.")

    update_dict = data.dict(exclude_unset=True)
    for k, v in update_dict.items():
        if v is not None:
            setattr(g, k, v)

    db.commit()
    db.refresh(g)

    admin_auth.log_admin_action(
        db, admin.username, "GAME_UPDATED",
        f"Updated arena challenge '{g.title}'",
        admin_auth.get_client_ip(request)
    )
    return {"status": "success", "game": g}


@admin_router.delete("/api/admin/games/{game_id}")
async def api_admin_delete_game(game_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete arena challenge."""
    admin = admin_auth.get_current_admin(request, db)
    g = db.query(models.GameChallenge).filter(models.GameChallenge.id == game_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Challenge not found.")

    title = g.title
    db.delete(g)
    db.commit()

    admin_auth.log_admin_action(
        db, admin.username, "GAME_DELETED",
        f"Deleted arena challenge '{title}'",
        admin_auth.get_client_ip(request)
    )
    return {"status": "success", "message": f"Challenge '{title}' deleted."}


# ==========================================
# 10. System Settings & Password Modification
# ==========================================

@admin_router.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings_page(request: Request, db: Session = Depends(get_db)):
    """Admin Settings & Security Configuration."""
    admin = admin_auth.get_current_admin(request, db)
    settings_records = db.query(models.SiteSettings).all()
    settings_dict = {s.key: s.value for s in settings_records}
    audit_logs = db.query(models.AdminAuditLog).order_by(models.AdminAuditLog.created_at.desc()).limit(50).all()

    return templates.TemplateResponse(
        request=request,
        name="admin/settings.html",
        context={
            "admin_user": admin,
            "active_page": "settings",
            "settings_dict": settings_dict,
            "audit_logs": audit_logs
        }
    )


@admin_router.post("/api/admin/update-credentials")
async def api_admin_update_credentials(data: models.AdminCredentialUpdate, request: Request, db: Session = Depends(get_db)):
    """
    Securely updates administrator username and/or password in Supabase PostgreSQL.
    Re-hashes with Argon2id and automatically refreshes the JWT cookie.
    """
    admin = admin_auth.get_current_admin(request, db)

    # 1. Verify current password
    if not admin_auth.verify_password(data.current_password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password entered is incorrect."
        )

    updated_fields = []
    old_username = admin.username

    # 2. Update Username if requested
    if data.new_username and data.new_username.strip():
        clean_user = data.new_username.strip()
        if len(clean_user) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New username must be at least 3 characters long."
            )
        if clean_user.lower() != admin.username.lower():
            existing = db.query(models.AdminUser).filter(
                func.lower(models.AdminUser.username) == clean_user.lower(),
                models.AdminUser.id != admin.id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Username '{clean_user}' is already taken. Please choose another."
                )
            admin.username = clean_user
            updated_fields.append(f"Username changed to '{clean_user}'")

    # 3. Update Password if requested
    if data.new_password and data.new_password.strip():
        clean_pwd = data.new_password.strip()
        if len(clean_pwd) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 6 characters long."
            )
        admin.password_hash = admin_auth.hash_password(clean_pwd)
        updated_fields.append("Password re-hashed with Argon2id and updated")

    if not updated_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No credential updates provided."
        )

    db.commit()
    db.refresh(admin)

    # 4. Log Action
    details_str = " & ".join(updated_fields)
    admin_auth.log_admin_action(
        db, admin.username, "CREDENTIALS_UPDATED",
        details_str,
        admin_auth.get_client_ip(request)
    )

    # 5. Issue updated JWT session cookie for the new username
    new_token = admin_auth.create_admin_token(admin.username)
    response = Response(
        content=json.dumps({
            "status": "success",
            "message": f"Successfully updated: {details_str}.",
            "username": admin.username
        }),
        media_type="application/json"
    )
    response.set_cookie(
        key="hwi_admin_token",
        value=new_token,
        httponly=True,
        samesite="lax",
        max_age=8 * 3600,
        path="/"
    )
    return response


@admin_router.post("/api/admin/change-password")
async def api_admin_change_password(data: models.AdminPasswordChange, request: Request, db: Session = Depends(get_db)):
    """Secure password modification endpoint with Argon2id re-hashing."""
    admin = admin_auth.get_current_admin(request, db)

    # Verify current password
    if not admin_auth.verify_password(data.current_password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password entered is incorrect."
        )

    # Validate new password
    if len(data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters long."
        )

    # Hash new password with Argon2id
    new_hash = admin_auth.hash_password(data.new_password)
    admin.password_hash = new_hash
    db.commit()

    admin_auth.log_admin_action(
        db, admin.username, "PASSWORD_CHANGED",
        "Administrator password successfully updated and re-hashed with Argon2id.",
        admin_auth.get_client_ip(request)
    )
    return {"status": "success", "message": "Password updated successfully."}


@admin_router.post("/api/admin/settings")
async def api_admin_save_settings(request: Request, db: Session = Depends(get_db)):
    """Save or update system configuration flags in site_settings table."""
    admin = admin_auth.get_current_admin(request, db)
    body = await request.json()
    items = body.get("settings", [])

    for item in items:
        k = item.get("key")
        v = item.get("value", "")
        desc = item.get("description", "")
        if not k:
            continue
        record = db.query(models.SiteSettings).filter(models.SiteSettings.key == k).first()
        if record:
            record.value = v
            record.updated_at = datetime.utcnow()
        else:
            record = models.SiteSettings(key=k, value=v, description=desc, updated_at=datetime.utcnow())
            db.add(record)

    db.commit()

    admin_auth.log_admin_action(
        db, admin.username, "SETTINGS_UPDATED",
        f"Updated {len(items)} system settings entries.",
        admin_auth.get_client_ip(request)
    )
    return {"status": "success", "message": "Settings updated successfully."}
