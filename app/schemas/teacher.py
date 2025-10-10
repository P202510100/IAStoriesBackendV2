from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class TeacherBase(BaseModel):
    current_school: Optional[str] = Field(None, max_length=255)
    alma_mater: Optional[str] = Field(None, max_length=255)
    degree_level: Optional[str] = Field(None, max_length=100)
    major: Optional[str] = Field(None, max_length=255)


class TeacherCreate(TeacherBase):
    user_id: int


class TeacherRead(TeacherBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class TeacherUpdate(TeacherBase):
    current_school: Optional[str] = None
    alma_mater: Optional[str] = None
    degree_level: Optional[str] = None
    major: Optional[str] = None
