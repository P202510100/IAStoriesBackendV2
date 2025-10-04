from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.models.models import Student
from app.services.ai_services import GamificationService, AIConfig

router = APIRouter()

@router.get("/levels")
def get_levels_info():
    return {
        "levels": AIConfig.LEVELS,
        "total_levels": len(AIConfig.LEVELS)
    }

@router.post("/complete-story")
def complete_story_gamification(
    student_id: int,
    correct_answers: int,
    total_questions: int,
    time_average: Optional[float] = None,
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    is_perfect = (correct_answers == total_questions)
    points_result = GamificationService.calculate_points(
        correct_answers=correct_answers,
        total_questions=total_questions,
        time_average=time_average,
        is_perfect=is_perfect
    )
    
    student.total_points += points_result["total_points"]
    level_info = GamificationService.calculate_level(student.total_points)
    old_level = student.current_level
    student.current_level = level_info["level"]
    
    db.commit()
    
    congratulation_msg = GamificationService.generate_congratulation_message(
        correct=correct_answers,
        total=total_questions,
        points=points_result["total_points"]
    )
    
    level_up = level_info["level"] > old_level
    level_up_message = None
    if level_up:
        level_up_message = f"¡INCREÍBLE! ¡Has alcanzado el nivel {level_info['level']}: {level_info['level_name']}! 🎉"
    
    return {
        "student_id": student_id,
        "points_earned": points_result,
        "congratulation_message": congratulation_msg,
        "level_info": level_info,
        "level_up": level_up,
        "level_up_message": level_up_message,
        "new_total_points": student.total_points
    }