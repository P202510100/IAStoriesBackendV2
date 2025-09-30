from pydantic import BaseModel, Field
from typing import Optional


class TeacherBase(BaseModel):
    current_school: Optional[str] = Field(None, max_length=255)
    alma_mater: Optional[str] = Field(None, max_length=255)
    degree_level: Optional[str] = Field(None, max_length=100)
    major: Optional[str] = Field(None, max_length=255)


class TeacherCreate(TeacherBase):
    pass


class TeacherRead(TeacherBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class TeacherUpdate(TeacherBase):
    pass
