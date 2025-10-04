from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AnswerBase(BaseModel):
    question_index: int
    response: str
    is_correct: Optional[bool] = None

class AnswerCreate(AnswerBase):
    pass

class AnswerRead(AnswerBase):
    id: int
    record_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True