from pydantic import BaseModel

class EnrollmentCreate(BaseModel):
    teacher_id: int
    student_id: int

class EnrollmentRead(BaseModel):
    id: int
    teacher_id: int
    student_id: int

    class Config:
        orm_mode = True
