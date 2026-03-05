from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.databases.database import SessionLocal
from app.models.visitor import Visitor
from app.utils.security import get_current_admin

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.get("/admin/stats")
async def get_stats(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin) # Protects this endpoint!
):
    visitors = db.query(Visitor).all()
    
    # Format data for your ECharts
    return {
        "total_visitors": len(visitors),
        "visitor_data": [
            {
                "name": v.name, 
                "count": v.visit_count, 
                "last_visit": v.last_visit
            } for v in visitors
        ]
    }