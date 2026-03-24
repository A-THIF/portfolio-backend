from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.databases.database import SessionLocal
from app.models.visitor import Visitor
from app.schemas.auth_schema import LoginRequest
from app.utils.security import create_access_token, get_current_user
from app.services.email_service import send_contact_email
from slowapi.util import get_remote_address
from slowapi import Limiter
import os

router = APIRouter()
ALERT_INTERVAL = timedelta(hours=6)
limiter = Limiter(key_func=get_remote_address)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/login")
@limiter.limit("5/minute")
async def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host
    user_agent = request.headers.get("user-agent")
    
    # --- ADMIN MASTER CHECK ---
    is_admin = data.name == os.getenv("ADMIN_NAME") and data.profile_link == os.getenv("ADMIN_SECRET_KEY")
    role = "admin" if is_admin else "visitor"

    visitor = db.query(Visitor).filter(
        Visitor.name == data.name,
        Visitor.ip_address == ip
    ).first()

    now = datetime.utcnow()
    should_alert = False

    if visitor:
        visitor.visit_count += 1
        visitor.last_visit = now
        if data.profile_link: 
            visitor.profile_link = data.profile_link

        if not visitor.last_alert or (now - visitor.last_alert) >= ALERT_INTERVAL:
            should_alert = True
    else:
        visitor = Visitor(
            name=data.name,
            profile_link=data.profile_link,
            ip_address=ip,
            user_agent=user_agent,
            visit_count=1,
            first_visit=now,
            last_visit=now
        )
        db.add(visitor)
        should_alert = True 

    if should_alert and not is_admin:
        visitor.last_alert = now
        db.commit()
        send_contact_email(
            name=visitor.name,
            profile_link=visitor.profile_link,
            visit_count=visitor.visit_count,
            ip=visitor.ip_address,
            agent=visitor.user_agent
        )
    else:
        db.commit()

    # JWT token for the frontend app
    token = create_access_token({"sub": data.name, "role": role})

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 3600,
        "role": role
    }

@router.get("/portfolio-data")
def get_private_data(current_user: dict = Depends(get_current_user)):
    return {
        "data": "Welcome to the gamified portfolio!", 
        "user": current_user['sub']
    }