from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    name: str
    password: str

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    name: str

    class Config:
        from_attributes = True
