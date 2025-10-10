from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime

from app.models.models import UserType


class StudentBase(BaseModel):
    birth_date: Optional[date] = None
    current_grade: Optional[str] = Field(None, max_length=50)
    interests: Optional[str] = None


class StudentCreate(StudentBase):
    user_id: int

class UserBase(BaseModel):
    id: int
    fullname: str
    email: str
    tipo: UserType

    model_config = ConfigDict(from_attributes=True)

class StudentRead(StudentBase):
    id: int
    user_id: int
    total_points: int
    last_updated_date: Optional[datetime]
    current_level: int
    user: UserBase

    model_config = ConfigDict(from_attributes=True)


class StudentDetail(BaseModel):
    id: int
    edad: Optional[int] = None
    current_grade: Optional[str]
    current_level: Optional[int]
    interests: Optional[str]
    total_points: int
    last_updated_date: Optional[datetime]
    user: UserBase

    model_config = ConfigDict(from_attributes=True)


class StudentUpdate(StudentBase):
    birth_date: Optional[date] = None
    current_grade: Optional[str] = None
    interests: Optional[str] = None
    current_level: Optional[int] = None
