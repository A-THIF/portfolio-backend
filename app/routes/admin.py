from fastapi import APIRouter, Depends, HTTPException, Request, Cookie
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.databases.database import SessionLocal
from app.models.visitor import Visitor
from app.utils.security import verify_token # Import the verification logic
import os
from user_agents import parse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.get("/admin/user/{user_id}", response_class=HTMLResponse)
async def get_user_detail(
    user_id: int, 
    db: Session = Depends(get_db), 
    admin_session: str = Cookie(None)
):
    # 1. Gatekeeper Check
    if not admin_session:
        return HTMLResponse(content="<h1>Unauthorized</h1>", status_code=401)
    
    payload = verify_token(admin_session)
    if not payload or payload.get("role") != "admin":
        return HTMLResponse(content="<h1>Forbidden</h1>", status_code=403)

    user = db.query(Visitor).filter(Visitor.id == user_id).first()
    if not user: 
        return HTMLResponse(content="<h1>User Not Found</h1>", status_code=404)

    # --- PARSING THE USER AGENT ---
    ua = parse(user.user_agent or "Unknown")
    browser_detail = f"{ua.browser.family} {ua.browser.version_string}"
    os_detail = f"{ua.os.family} {ua.os.version_string}"
    
    # Determine the device category
    if ua.is_mobile:
        device_type = "📱 Mobile"
    elif ua.is_tablet:
        device_type = "📟 Tablet"
    elif ua.is_bot:
        device_type = "🤖 Bot/Scanner"
    else:
        device_type = "💻 Desktop"

    html_content = f"""
    <html>
      <head>
        <title>User {user.name} - Details</title>
        <style>
          body {{ font-family: sans-serif; background: #0a0a0a; color: #fff; padding: 40px; display: flex; flex-direction: column; align-items: center; }}
          .card {{ background: #111; border: 1px solid #333; padding: 25px; border-radius: 12px; width: 100%; max-width: 600px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
          .row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #222; }}
          .label {{ color: #888; font-weight: bold; font-size: 13px; text-transform: uppercase; }}
          .value {{ color: #4CAF50; font-family: monospace; }}
          .ua-box {{ background: #000; padding: 10px; font-size: 11px; color: #555; border-radius: 4px; margin-top: 15px; word-break: break-all; }}
          .back {{ margin-top: 20px; color: #00BFFF; text-decoration: none; }}
        </style>
      </head>
      <body>
        <div class="card">
          <h1 style="color:#4CAF50; margin-top:0;">Profile: {user.name}</h1>
          <div class="row"><span class="label">Email</span><span class="value">{user.email or '---'}</span></div>
          <div class="row"><span class="label">IP Address</span><span class="value">{user.ip_address}</span></div>
          <div class="row"><span class="label">Total Visits</span><span class="value">{user.visit_count}</span></div>
          <div class="row"><span class="label">Last Seen</span><span class="value">{user.last_visit.strftime('%Y-%m-%d %H:%M') if user.last_visit else 'N/A'}</span></div>
          
          <h3 style="color:#888; margin: 20px 0 10px 0;">Device Analysis</h3>
          <div class="row"><span class="label">Platform</span><span class="value">{device_type}</span></div>
          <div class="row"><span class="label">OS</span><span class="value">{os_detail}</span></div>
          <div class="row"><span class="label">Browser</span><span class="value">{browser_detail}</span></div>
          
          <div class="row" style="border:none;"><span class="label">Profile Link</span><span class="value">{user.profile_link or 'None'}</span></div>
          
          <div class="ua-box"><strong>Raw User-Agent:</strong><br>{user.user_agent}</div>
        </div>
        <a href="/admin-dashboard/view" class="back">&larr; Back to Dashboard</a>
      </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get("/public/stats")
async def get_public_stats(db: Session = Depends(get_db)):
    stats = db.query(
        func.date(Visitor.last_visit).label('date'),
        func.count(Visitor.id).label('count')
    ).group_by(func.date(Visitor.last_visit))\
     .order_by(func.date(Visitor.last_visit)).all()

    total = db.query(func.count(Visitor.id)).scalar()
    return {
        "dates": [str(s.date) for s in stats],
        "counts": [s.count for s in stats],
        "total_visitors": total
    }
