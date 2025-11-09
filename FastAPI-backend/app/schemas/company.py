from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None

class CompanyCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class CompanyOut(CompanyBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class CompanyRead(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = {"from_attributes": True} 