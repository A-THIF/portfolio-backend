# app/routes/auth.py
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.databases.database import SessionLocal
from app.models.visitor import Visitor
from app.schemas.auth_schema import LoginRequest
from app.utils.security import create_access_token
from app.services.email_service import send_contact_email
from app.utils.security import get_current_user
from slowapi.util import get_remote_address
from slowapi import Limiter


router = APIRouter()
ALERT_INTERVAL = timedelta(hours=6)  # 6-hour gap between emails

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()
limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
async def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host
    user_agent = request.headers.get("user-agent")

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

        # Send email only if last_alert is None or >6 hours ago
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
        should_alert = True  # always alert for new visitor

    if should_alert:
        visitor.last_alert = now  # update alert time
        db.commit()  # commit before sending email to ensure DB is updated

        # Prepare email with visit count
        alert_msg = f"Visitor: {visitor.name}\nTotal Visits: {visitor.visit_count}\nLast visit: {visitor.last_visit}"
        send_contact_email(visitor.name, visitor.profile_link or "No link provided")
    else:
        db.commit()  # just commit DB updates

    # JWT token creation
    token = create_access_token({"sub": data.name})

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 3600,
        "visit_count": visitor.visit_count
    }

@router.get("/portfolio-data") # Use router, not app
def get_private_data(current_user: dict = Depends(get_current_user)):
    return {
        "data": "Welcome to the gamified portfolio!", 
        "user": current_user['sub']
    }