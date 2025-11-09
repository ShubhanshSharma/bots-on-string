from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChatbotBase(BaseModel):
    name: str
    description: Optional[str] = None

class ChatbotCreate(BaseModel):
    name: str
    description: Optional[str] = None
    company_id: int

class ChatbotUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ChatbotOut(ChatbotBase):
    id: int
    company_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class ChatbotRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    company_id: int

    model_config = {"from_attributes": True}