import datetime
from time import timezone
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class Visitor(Base):
    __tablename__ = "visitors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, default=lambda: datetime.now(timezone.utc) + datetime.timedelta(days=7))  # 👈 add this
    # Relationships
    sessions = relationship("VisitorSession", back_populates="visitor")
    # ✅ Remove direct import and use string name for lazy loading
    chatbots = relationship("Chatbot", secondary="visitor_sessions", viewonly=True)
