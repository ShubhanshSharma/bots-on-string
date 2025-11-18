from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

class CompanyLogin(BaseModel):
    email: str
    password: str

class CompanyBase(BaseModel):
    name: str
    email: EmailStr
    description: Optional[str] = None

class CompanyCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    description: Optional[str] = None

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    description: Optional[str] = None


class CompanyOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    description: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


    class Config:
        orm_mode = True

class CompanyRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    description: Optional[str] = None

    model_config = {"from_attributes": True}
