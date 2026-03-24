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

    # We force HTML response here so you don't see JSON in the browser
    html_content = f"""
    <html>
      <head>
        <title>User {user.name} - Details</title>
        <style>
          body {{ font-family: sans-serif; background: #0a0a0a; color: #fff; padding: 40px; display: flex; flex-direction: column; align-items: center; }}
          .card {{ background: #111; border: 1px solid #333; padding: 25px; border-radius: 12px; width: 100%; max-width: 600px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
          .row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #222; }}
          .label {{ color: #888; font-weight: bold; font-size: 13px; }}
          .value {{ color: #4CAF50; font-family: monospace; }}
          .back {{ margin-top: 20px; color: #00BFFF; text-decoration: none; }}
        </style>
      </head>
      <body>
        <div class="card">
          <h1>Profile: {user.name}</h1>
          <div class="row"><span class="label">IP Address</span><span class="value">{user.ip_address}</span></div>
          <div class="row"><span class="label">Total Visits</span><span class="value">{user.visit_count}</span></div>
          <div class="row"><span class="label">Last Seen</span><span class="value">{user.last_visit.strftime('%Y-%m-%d %H:%M') if user.last_visit else 'N/A'}</span></div>
          <div class="row"><span class="label">User-Agent</span><span class="value" style="font-size:10px; text-align:right;">{user.user_agent}</span></div>
          <div class="row" style="border:none;"><span class="label">Profile Link</span><span class="value">{user.profile_link or 'None'}</span></div>
        </div>
        <a href="/admin-dashboard?token={token}" class="back">&larr; Back to Dashboard</a>
      </body>
    </html>
    """
    return HTMLResponse(content=html_content)
