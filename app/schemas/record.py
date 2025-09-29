from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional
from datetime import datetime

class RecordBase(BaseModel):
    story_id: int
    correct_answers: int = Field(..., ge=0)
    total_questions: int = Field(..., ge=0)
    points: Optional[int] = Field(None, ge=0)

    @model_validator(mode="after")
    def check_answers(self):
        if self.correct_answers is not None and self.total_questions is not None:
            if self.correct_answers > self.total_questions:
                raise ValueError("correct_answers no puede ser mayor que total_questions")
        return self


class RecordCreate(RecordBase):
    pass


class RecordRead(RecordBase):
    id: int
    student_id: int
    completed_at: datetime

    model_config = ConfigDict(from_attributes=True)  # reemplaza orm_mode
