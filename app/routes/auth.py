import os
from datetime import datetime, timedelta, timezone
from typing import Generator
from fastapi import APIRouter, Depends, Request, HTTPException, status, Response
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.databases.database import SessionLocal
from app.models.visitor import Visitor
from app.schemas.auth_schema import LoginRequest
from app.utils.security import create_access_token, get_current_user 
from app.services.telegram_service import send_visitor_notification

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

ALERT_INTERVAL = timedelta(hours=6)
ADMIN_SECRET_PLACEHOLDER = "[redacted]"

def get_db() -> Generator:
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/login")
@limiter.limit("5/minute")
async def login(data: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    ip = request.client.host
    user_agent = request.headers.get("user-agent")
    
    # 1. Identity Check
    is_admin = (data.name == os.getenv("ADMIN_NAME") and data.profile_link == os.getenv("ADMIN_SECRET_KEY"))
    role = "admin" if is_admin else "visitor"
    
    # 2. Database Logic (Stats/Alerts)
    stored_profile_link = ADMIN_SECRET_PLACEHOLDER if is_admin else data.profile_link
    visitor = db.query(Visitor).filter(Visitor.name == data.name, Visitor.ip_address == ip).first()
    
    # --- CRITICAL FIX: NAIVE DATETIME FOR DATABASE COMPATIBILITY ---
    now = datetime.now(timezone.utc).replace(tzinfo=None) 
    
    should_alert = False

    if visitor:
        visitor.visit_count += 1
        visitor.last_visit = now
        if not is_admin: 
            visitor.profile_link = stored_profile_link

        if not visitor.last_alert or (now - visitor.last_alert) >= ALERT_INTERVAL:
            should_alert = True
    else:
        visitor = Visitor(
            name=data.name, 
            email=data.email,  # <--- ADD THIS LINE
            profile_link=stored_profile_link, 
            ip_address=ip,
            user_agent=user_agent, 
            visit_count=1, 
            first_visit=now, 
            last_visit=now,
            last_alert=now if not is_admin else None
        )
        db.add(visitor)
        should_alert = True

    db.commit()

    # 3. Notification Logic
    # 3. Notification Logic
    if should_alert and not is_admin:
        visitor.last_alert = now
        db.commit()
        # FIX: Changed from send_contact_email to send_visitor_notification
        # Note the 'await' keyword and adding the 'email' field
        await send_visitor_notification(
            name=visitor.name, 
            email=getattr(data, 'email', 'N/A'), # Assuming email is in your LoginRequest schema
            profile_link=visitor.profile_link,
            visit_count=visitor.visit_count, 
            ip=visitor.ip_address
        )

    # 4. Token & Cookie Logic (The Hidden Signal)
    # C:\Users\parve\Documents\Projects\portfolio-backend\app\routes\auth.py

    # ... (inside your login function)
    token = create_access_token({"sub": data.name, "role": role})
    
    if role == "admin":
        response.set_cookie(
            key="admin_session", # MUST match the name in security.py
            value=token,
            httponly=True,
            samesite="none",  # REQUIRED for Vercel -> Render
            secure=True,      # REQUIRED for samesite="none"
            max_age=3600,
            path="/"          # REQUIRED so the whole domain can see it
        )

    return {
        "access_token": token,
        "role": role,
        "token_type": "bearer",
        "expires_in": 3600
    }

@router.get("/portfolio-data")
def get_private_data(current_user: dict = Depends(get_current_user)):
    return {
        "data": "Welcome to the gamified portfolio!", 
        "user": current_user['sub']
    }