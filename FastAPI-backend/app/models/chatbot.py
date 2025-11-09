# app/models/chatbot.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base

class Chatbot(Base):
    __tablename__ = "chatbots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)

    company = relationship("Company", back_populates="chatbots")
    sessions = relationship("VisitorSession", back_populates="chatbot", cascade="all, delete-orphan")
    chats = relationship("Chat", back_populates="chatbot", cascade="all, delete-orphan")