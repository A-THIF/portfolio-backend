from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.databases.database import SessionLocal
from app.models.visitor import Visitor
from app.utils.security import get_current_admin
import os
from sqlalchemy import func

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.get("/admin/stats")
async def get_stats(db: Session = Depends(get_db), token: str = Query(None)):
    if token != os.getenv("ADMIN_SECRET_KEY"):
        raise HTTPException(status_code=401)

    # Grouping by Date so the graph is clean
    stats = db.query(
        func.date(Visitor.last_visit).label('date'),
        func.count(Visitor.id).label('count')
    ).group_by(func.date(Visitor.last_visit))\
     .order_by(func.date(Visitor.last_visit)).all()

    return {
        "dates": [str(s.date) for s in stats],
        "counts": [s.count for s in stats]
    }


@router.get("/admin/user/{user_id}", response_class=HTMLResponse)
async def get_user_detail(user_id: int, request: Request, db: Session = Depends(get_db), token: str = Query(None)):
    if token != os.getenv("ADMIN_SECRET_KEY"):
        raise HTTPException(status_code=401)

    user = db.query(Visitor).filter(Visitor.id == user_id).first()
    if not user: 
        return HTMLResponse(content="<h1>User Not Found</h1>", status_code=404)

    if "text/html" in request.headers.get("accept", ""):
        html_content = f"""
        <html>
          <head>
            <title>User {user.name} - Details</title>
            <style>
              body {{ font-family: Arial, sans-serif; background: #111; color: #fff; padding: 25px; }}
              .card {{ background: #222; border: 1px solid #444; padding: 20px; border-radius: 8px; max-width: 800px; }}
              .row {{ margin-bottom: 8px; }}
              .label {{ color: #ccc; width: 140px; display: inline-block; }}
              .value {{ color: #fff; }}
              a {{ color: #59a6ff; text-decoration: none; }}
            </style>
          </head>
          <body>
            <h1>User Profile: {user.name}</h1>
            <div class="card">
              <div class="row"><span class="label">ID:</span><span class="value">{user.id}</span></div>
              <div class="row"><span class="label">Name:</span><span class="value">{user.name}</span></div>
              <div class="row"><span class="label">Profile:</span><span class="value">{user.profile_link or '—'}</span></div>
              <div class="row"><span class="label">Email:</span><span class="value">{user.email or '—'}</span></div>
              <div class="row"><span class="label">IP Address:</span><span class="value">{user.ip_address}</span></div>
              <div class="row"><span class="label">User-Agent:</span><span class="value">{user.user_agent}</span></div>
              <div class="row"><span class="label">Visits:</span><span class="value">{user.visit_count}</span></div>
              <div class="row"><span class="label">First Seen:</span><span class="value">{user.first_visit}</span></div>
              <div class="row"><span class="label">Last Seen:</span><span class="value">{user.last_visit}</span></div>
              <div class="row"><span class="label">Last Alert:</span><span class="value">{user.last_alert or '—'}</span></div>
            </div>
            <p><a href="/admin-dashboard?token={token}">&larr; Back to dashboard</a></p>
          </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    # Fallback: Return JSON if it's an API call, not a browser visit
    return {
        "id": user.id,
        "name": user.name,
        "ip_address": user.ip_address,
        "visit_count": user.visit_count,
        "last_visit": user.last_visit.isoformat() if user.last_visit else None
    }