path = r"C:\Users\saad uddin\.gemini\antigravity\scratch\hack-with-india-mcet\main.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

target = """    sessions = query.order_by(models.SessionItem.order_num.asc()).all()
    return sessions"""

replacement = """    sessions = query.order_by(models.SessionItem.order_num.asc()).all()
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
    return {"status": "success", "message": f"Event {event_id} deleted successfully"}"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS")
else:
    print("TARGET NOT FOUND")
