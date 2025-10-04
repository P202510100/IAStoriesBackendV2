from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

from app.models.models import UserType


class StudentBase(BaseModel):
    birth_date: Optional[date]
    current_grade: Optional[str] = Field(None, max_length=50)
    interests: Optional[str]


class StudentCreate(StudentBase):
    pass

class UserBase(BaseModel):
    id: int
    fullname: str
    email: str
    tipo: UserType

    class Config:
        from_attributes = True

class StudentRead(StudentBase):
    id: int
    user_id: int
    total_points: int
    last_updated_date: Optional[datetime]
    current_level: int
    user: UserBase

    class Config:
        from_attributes = True

class StudentDetail(BaseModel):
    id: int
    edad: Optional[int] = None
    current_grade: Optional[str]
    current_level: Optional[int]
    interests: Optional[str]
    total_points: int
    last_updated_date: Optional[datetime]
    user: UserBase  # relación incluida

    class Config:
        orm_mode = True

class StudentUpdate(StudentBase):
    birth_date: Optional[date] = None
    current_grade: Optional[str] = None
    interests: Optional[str] = None
    current_level: Optional[int] = None
