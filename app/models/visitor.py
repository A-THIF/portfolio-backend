# app/models/visitor.py
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.databases.database import Base

class Visitor(Base):
    __tablename__ = "visitors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    profile_link = Column(String, nullable=True) # Optional
    email = Column(String, nullable=True)        # Optional
    ip_address = Column(String)
    user_agent = Column(String)
    first_visit = Column(DateTime, default=datetime.utcnow)
    last_visit = Column(DateTime, default=datetime.utcnow)
    visit_count = Column(Integer, default=1)    
    last_alert = Column(DateTime, nullable=True)  # Track last email alert times