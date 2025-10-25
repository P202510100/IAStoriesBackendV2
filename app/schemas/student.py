from pydantic import BaseModel, Field, ConfigDict, computed_field
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
    created_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)

class StudentRead(StudentBase):
    id: int
    user_id: int
    total_points: int
    last_updated_date: Optional[datetime]
    current_level: int
    user: UserBase

    model_config = ConfigDict(from_attributes=True)


class StudentDetail(StudentBase):
    id: int
    current_grade: Optional[str]
    current_level: Optional[int]
    interests: Optional[str]
    total_points: int
    last_updated_date: Optional[datetime]
    user: UserBase

    model_config = ConfigDict(from_attributes=True)

    @computed_field(return_type=int | None)
    def edad(self) -> Optional[int]:
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None


class StudentUpdate(StudentBase):
    birth_date: Optional[date] = None
    current_grade: Optional[str] = None
    interests: Optional[str] = None
    current_level: Optional[int] = None
