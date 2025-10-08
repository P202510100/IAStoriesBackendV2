from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)
