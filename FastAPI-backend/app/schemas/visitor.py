from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class VisitorBase(BaseModel):
    session_id: str

class VisitorCreate(BaseModel):
    anonymous_id: Optional[str] = None

class VisitorOut(VisitorBase):
    id: int
    chatbot_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class VisitorRead(BaseModel):
    id: int
    anonymous_id: Optional[str]
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}