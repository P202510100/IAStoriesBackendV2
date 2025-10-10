from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class StoryBase(BaseModel):
    title: str = Field(..., max_length=255)
    content: Optional[str]
    topic: Optional[str]
    question_answer: Optional[List[Dict[str, Any]]]
    story_metadata: Optional[Dict[str, Any]]
    characters: Optional[List[str]]

class StoryCreate(StoryBase):
    student_id: Optional[int]

class StoryRead(StoryBase):
    id: int
    created_at: datetime
    image_b64: Optional[str] = None
    record_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class StoryUpdate(StoryBase):
    pass

class StoryGenerateRequest(BaseModel):
    user_id: int
    nombre: str
    edad: int
    elementos: str
    topic: str
