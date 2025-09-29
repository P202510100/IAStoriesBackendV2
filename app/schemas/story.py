from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class StoryBase(BaseModel):
    title: str = Field(..., max_length=255)
    content: Optional[str]
    topic: Optional[str]
    question_answer: Optional[str]
    story_metadata: Optional[str]
    characters: Optional[str]

class StoryCreate(StoryBase):
    alumno_id: Optional[int]

class StoryRead(StoryBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class StoryUpdate(StoryBase):
    pass
