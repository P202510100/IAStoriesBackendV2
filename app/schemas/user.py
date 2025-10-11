from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime, date
from app.models.models import UserType
from app.schemas.student import StudentRead, StudentUpdate
from app.schemas.teacher import TeacherRead, TeacherUpdate


# Perfil estudiante
class StudentProfileCreate(BaseModel):
    birth_date: Optional[date] = None
    current_grade: Optional[str] = None
    interests: Optional[str] = None


# Perfil profesor
class TeacherProfileCreate(BaseModel):
    current_school: Optional[str] = None
    alma_mater: Optional[str] = None
    degree_level: Optional[str] = None
    major: Optional[str] = None

class UserBase(BaseModel):
    fullname: str = Field(..., min_length=1, max_length=255)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    tipo: Optional[UserType] = UserType.student
    student_profile: Optional[StudentProfileCreate] = None
    teacher_profile: Optional[TeacherProfileCreate] = None

class EmailRequest(BaseModel):
    email: EmailStr


class PasswordResetRequest(BaseModel):
    email: EmailStr
    new_password: str

class UserRead(UserBase):
    id: int
    tipo: UserType
    created_at: datetime
    activo: bool

    student_profile: Optional[StudentRead] = None
    teacher_profile: Optional[TeacherRead] = None

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    fullname: Optional[str]
    activo: Optional[bool]
    email: Optional[EmailStr] = None
    student_profile: Optional[StudentUpdate] = None
    teacher_profile: Optional[TeacherUpdate] = None

class PasswordChangeRequest(BaseModel):
    user_id: int = Field(..., description="ID del usuario")
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)

class MessageResponse(BaseModel):
    message: str
