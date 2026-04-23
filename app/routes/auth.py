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
from app.utils.security import create_access_token
from app.services.email_service import send_contact_email

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
    now = datetime.now(timezone.utc)
    should_alert = False

    if visitor:
        visitor.visit_count += 1
        visitor.last_visit = now
        if not is_admin: visitor.profile_link = stored_profile_link
        if not visitor.last_alert or (now - visitor.last_alert) >= ALERT_INTERVAL:
            should_alert = True
    else:
        visitor = Visitor(
            name=data.name, profile_link=stored_profile_link, ip_address=ip,
            user_agent=user_agent, visit_count=1, first_visit=now, last_visit=now
        )
        db.add(visitor)
        should_alert = True 

    db.commit()

    # 3. Notification Logic
    if should_alert and not is_admin:
        visitor.last_alert = now
        db.commit()
        send_contact_email(
            name=visitor.name, profile_link=visitor.profile_link,
            visit_count=visitor.visit_count, ip=visitor.ip_address, agent=visitor.user_agent
        )

    # 4. Token & Cookie Logic
    token = create_access_token({"sub": data.name, "role": role})
    
    if role == "admin":
        response.set_cookie(
            key="admin_session",
            value=token,
            httponly=True,
            samesite="lax",
            secure=True 
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
