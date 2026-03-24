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
from sqlalchemy import func

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

    # We don't need to email alerts for your own admin logins
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
async def get_admin_stats(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    last_7_days = datetime.utcnow() - timedelta(days=7)

    results = db.query(
        func.date(Visitor.last_visit).label("date"),
        func.count(Visitor.id).label("count")
    ).filter(
        Visitor.last_visit >= last_7_days
    ).group_by(
        func.date(Visitor.last_visit)
    ).order_by(
        func.date(Visitor.last_visit)
    ).all()

    return {
        "dates": [str(r.date) for r in results],
        "counts": [r.count for r in results]
    }

@router.get("/portfolio-data")
def get_private_data(current_user: dict = Depends(get_current_user)):
    return {
        "data": "Welcome to the gamified portfolio!", 
        "user": current_user['sub']
    }

@router.get("/admin/users")
def get_users(page: int = 1, limit: int = 10, db: Session = Depends(get_db), request: Request = None):
    token = request.query_params.get("token")
    if token != os.getenv("ADMIN_SECRET_KEY"):
        raise HTTPException(status_code=401)

    offset = (page - 1) * limit

    users = db.query(Visitor)\
        .order_by(Visitor.last_visit.desc())\
        .offset(offset)\
        .limit(limit)\
        .all()

    total = db.query(Visitor).count()

    return {
        "total": total,
        "page": page,
        "data": [
            {
                "id": u.id,
                "name": u.name,
                "visits": u.visit_count,
                "last_visit": u.last_visit
            } for u in users
        ]
    }

@router.get("/admin/user/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), request: Request = None):
    token = request.query_params.get("token")
    
    if token != os.getenv("ADMIN_SECRET_KEY"):
        raise HTTPException(status_code=401)

    user = db.query(Visitor).filter(Visitor.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "name": user.name,
        "profile": user.profile_link,
        "ip": user.ip_address,
        "browser": user.user_agent,
        "first_visit": user.first_visit,
        "last_visit": user.last_visit,
        "visits": user.visit_count
    }