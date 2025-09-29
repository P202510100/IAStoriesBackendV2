from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.models import UserType

class UserBase(BaseModel):
    fullname: str = Field(..., min_length=1, max_length=255)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    tipo: Optional[UserType] = UserType.student

class UserRead(UserBase):
    id: int
    tipo: UserType
    created_at: datetime
    activo: bool

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    fullname: Optional[str]
    activo: Optional[bool]
