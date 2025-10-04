from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.services.story_service import StoryService
from app.schemas.story import StoryCreate, StoryRead
from app.models.models import Story, Student
from app.services.ai_services import (
    StoryGenerationService,
    QuestionGenerationService,
    ImageGenerationService,
    PromptPersonalizationService
)

router = APIRouter()

@router.post("/", response_model=StoryRead)
def create_story(payload: StoryCreate, db: Session = Depends(get_db)):
    return StoryService.create_story(db, payload.dict())

@router.get("/", response_model=List[StoryRead])
def list_stories(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return StoryService.list_stories(db, skip, limit)

@router.get("/themes")
def get_available_themes():
    return {"themes": PromptPersonalizationService.get_available_themes()}

@router.post("/{story_id}/generate-images")
def generate_story_images(story_id: int, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Historia no encontrada")
    
    image_service = ImageGenerationService()
    
    try:
        image_url = image_service.generate_character_image(
            character_name=story.characters or "Héroe",
            theme=story.topic or "aventura",
            story_context=story.content[:200] if story.content else ""
        )
        
        return {
            "story_id": story_id,
            "images": {"main_character": image_url},
            "message": "Imágenes generadas exitosamente"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando imágenes: {str(e)}")

@router.post("/generate-ai")
def generate_story_with_ai(
    theme: str,
    character_name: str,
    student_id: int,
    age: int = 8,
    interests: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    story_service = StoryGenerationService()
    
    try:
        story_data = story_service.generate_story(
            theme=theme,
            character_name=character_name,
            age=age,
            interests=interests
        )
        
        new_story = Story(
            title=story_data["title"],
            content=story_data["content"],
            topic=theme,
            characters=", ".join(story_data["characters"]),
            story_metadata=str(story_data["metadata"]),
            alumno_id=student_id,
            created_at=datetime.utcnow()
        )
        
        db.add(new_story)
        db.commit()
        db.refresh(new_story)
        
        question_service = QuestionGenerationService()
        questions_data = question_service.generate_questions(
            story_content=story_data["content"],
            character_name=character_name
        )
        
        return {
            "id": new_story.id,
            "title": story_data["title"],
            "content": story_data["content"],
            "theme": theme,
            "character": character_name,
            "questions": questions_data,
            "message": "Historia generada exitosamente"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error generando historia: {str(e)}")