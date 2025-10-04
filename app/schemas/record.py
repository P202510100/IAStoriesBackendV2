from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from .story import StoryRead

class AnswerRead(BaseModel):
    id: int
    question_index: int
    response: str
    is_correct: Optional[bool]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

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

class RecordUpdate(BaseModel):
    correct_answers: Optional[int] = Field(None, ge=0)
    total_questions: Optional[int] = Field(None, ge=0)
    points: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(IN_PROGRESS|COMPLETED)$")

    @model_validator(mode="after")
    def validate_answers(self):
        if (
            self.correct_answers is not None
            and self.total_questions is not None
            and self.correct_answers > self.total_questions
        ):
            raise ValueError("correct_answers no puede ser mayor que total_questions")
        return self

class RecordCreate(RecordBase):
    pass


class RecordRead(RecordBase):
    id: int
    story_id: int
    student_id: int
    points: int
    correct_answers: int
    total_questions: int
    completed_at: Optional[datetime] = None
    status: str   # 👈 IN_PROGRESS o COMPLETED
    story: Optional["StoryRead"]
    answers: List[AnswerRead]

    model_config = ConfigDict(from_attributes=True)
