# app/models/visitor.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timedelta

class Visitor(Base):
    __tablename__ = "visitors"

    id = Column(Integer, primary_key=True, index=True)
    anonymous_id = Column(String(255), unique=True, index=True)  # random token for visitor
    created_at = Column(DateTime, default=datetime.utcnow)
    # sessions relationship via VisitorSession
    sessions = relationship("VisitorSession", back_populates="visitor", cascade="all, delete-orphan")
