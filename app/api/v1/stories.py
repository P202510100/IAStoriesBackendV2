from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas import StoryGenerateRequest
from app.services.story_service import StoryService
from app.schemas.story import StoryCreate, StoryRead

router = APIRouter()

@router.post("/", response_model=StoryRead)
def create_story(payload: StoryCreate, db: Session = Depends(get_db)):
    return StoryService.create_story(db, payload.dict())

@router.get("/", response_model=List[StoryRead])
def list_stories(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return StoryService.list_stories(db, skip, limit)

@router.post("/generate", response_model=StoryRead)
def generate_story(payload: StoryGenerateRequest, db: Session = Depends(get_db)):
    return StoryService.generate_story(db, payload)

@router.get("/student/{student_id}", response_model=List[StoryRead])
def list_stories_by_student(student_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return StoryService.list_stories_by_student(db, student_id, skip, limit)
