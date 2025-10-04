from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import random

from app.db.database import get_db
from app.models.models import Student
from app.services.ai_services import GamificationService

router = APIRouter()

@router.post("/answer")
def answer_question(
    question_id: int,
    student_id: int,
    selected_option: int,
    time_spent: Optional[float] = None,
    db: Session = Depends(get_db)
):
    is_correct = selected_option == 0
    points_earned = 20 if is_correct else 0
    
    student = db.query(Student).filter(Student.id == student_id).first()
    if student:
        student.total_points += points_earned
        level_info = GamificationService.calculate_level(student.total_points)
        student.current_level = level_info["level"]
        db.commit()
    
    return {
        "question_id": question_id,
        "is_correct": is_correct,
        "points_earned": points_earned,
        "can_retry": not is_correct,
        "explanation": "Esta es la respuesta correcta porque...",
        "student_total_points": student.total_points if student else 0,
        "student_level": student.current_level if student else 1
    }

@router.post("/{question_id}/retry")
def retry_question(question_id: int, student_id: int, db: Session = Depends(get_db)):
    messages = [
        "¡No te preocupes! Los grandes lectores también se equivocan 😊",
        "¡Inténtalo de nuevo! Estás aprendiendo y eso es lo importante 🌟",
        "¡Piénsalo bien! Estoy seguro de que esta vez lo lograrás 💪"
    ]
    
    return {
        "question_id": question_id,
        "can_retry": True,
        "attempt_number": 2,
        "motivational_message": random.choice(messages),
        "points_reduced": True,
        "new_points_value": 10
    }