from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.databases.database import SessionLocal
from app.models.visitor import Visitor
from app.schemas.auth_schema import LoginRequest
from app.utils.security import create_access_token, get_current_user, get_current_admin # Add this
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
    # Replace 'AthifMaster' and 'your_secret_link' with values only you know
    is_admin = data.name == "AthifMaster" and data.profile_link == "your_secret_link"
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

    # We don't need to email alerts for your own admin logins
    if should_alert and not is_admin:
        visitor.last_alert = now
        db.commit()
        send_contact_email(visitor.name, visitor.profile_link or "No link provided")
    else:
        db.commit()

    # JWT now includes the 'role'
    token = create_access_token({"sub": data.name, "role": role})

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 3600,
        "role": role
    }

# --- NEW ADMIN STATS ENDPOINT ---
@router.get("/admin/stats")
async def get_admin_stats(db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    """
    Only accessible if JWT has role: admin
    """
    visitors = db.query(Visitor).all()
    
    # This structure is perfect for ECharts
    return {
        "summary": {
            "total_visitors": len(visitors),
            "total_sessions": sum(v.visit_count for v in visitors)
        },
        "details": [
            {
                "name": v.name,
                "visits": v.visit_count,
                "last_active": v.last_visit,
                "platform": v.user_agent[:20] # Short version for charts
            } for v in visitors
        ]
    }

@router.get("/portfolio-data")
def get_private_data(current_user: dict = Depends(get_current_user)):
    return {
        "data": "Welcome to the gamified portfolio!", 
        "user": current_user['sub']
    }