from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class StudentBase(BaseModel):
    birth_date: Optional[date]
    current_grade: Optional[str] = Field(None, max_length=50)
    interests: Optional[str]

class StudentCreate(StudentBase):
    pass

class StudentRead(StudentBase):
    id: int
    user_id: int
    total_points: int
    last_updated_date: Optional[datetime]
    current_level: int

    class Config:
        orm_mode = True

class StudentUpdate(StudentBase):
    current_level: Optional[int]
