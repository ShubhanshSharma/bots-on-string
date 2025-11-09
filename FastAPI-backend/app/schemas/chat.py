from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChatBase(BaseModel):
    question: str
    answer: Optional[str] = None

class ChatCreate(BaseModel):
    visitor_session_id: Optional[int] = None
    chatbot_id: Optional[int] = None
    role: str
    message: str

class ChatOut(ChatBase):
    id: int
    visitor_id: int
    chatbot_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class ChatRead(BaseModel):
    id: int
    visitor_session_id: Optional[int]
    chatbot_id: Optional[int]
    role: str
    message: str
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}