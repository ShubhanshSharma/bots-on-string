# app/models/visitor_session.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timedelta

class VisitorSession(Base):
    __tablename__ = "visitor_sessions"

    id = Column(Integer, primary_key=True, index=True)
    visitor_id = Column(Integer, ForeignKey("visitors.id", ondelete="CASCADE"), nullable=False)
    chatbot_id = Column(Integer, ForeignKey("chatbots.id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

     # ✅ This is the missing relationship
    chats = relationship("Chat", back_populates="visitor_session", cascade="all, delete-orphan")

    # optional relationships to visitor and chatbot
    visitor = relationship("Visitor", back_populates="sessions", lazy="joined")
    chatbot = relationship("Chatbot", back_populates="sessions", lazy="joined")