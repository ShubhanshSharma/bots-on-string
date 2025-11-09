# app/models/chat.py
from __future__ import annotations
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

# import your project's Base
from app.db.base import Base

# Use TYPE_CHECKING to avoid runtime circular imports when referencing types
if TYPE_CHECKING:
    from app.models.visitor_session import VisitorSession  # for type hints only
    from app.models.chatbot import Chatbot

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    visitor_session_id = Column(Integer, ForeignKey("visitor_sessions.id"), nullable=True)
    chatbot_id = Column(Integer, ForeignKey("chatbots.id"), nullable=True)

    # role can be 'user'|'bot' etc.
    role = Column(String(20), nullable=False, default="user")
    message = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships (string form to avoid import-time circular issues)
    visitor_session = relationship("VisitorSession", back_populates="chats", foreign_keys=[visitor_session_id], lazy="joined")
    chatbot = relationship("Chatbot", back_populates="chats", foreign_keys=[chatbot_id], lazy="joined")
