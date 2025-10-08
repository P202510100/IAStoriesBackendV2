from pydantic import BaseModel, ConfigDict

class EnrollmentCreate(BaseModel):
    teacher_id: int
    student_id: int

class EnrollmentRead(BaseModel):
    id: int
    teacher_id: int
    student_id: int

    model_config = ConfigDict(from_attributes=True)


