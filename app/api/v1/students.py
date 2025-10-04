from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from app.db.database import get_db
from app.services.student_service import StudentService
from app.schemas.student import StudentRead, StudentUpdate
from app.models.models import Student, Story, Enrollment
from app.services.ai_services import GamificationService

router = APIRouter()

@router.get("/{user_id}", response_model=StudentRead)
def get_student(user_id: int, db: Session = Depends(get_db)):
    student = StudentService.get_by_user_id(db, user_id)
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return student

@router.put("/{user_id}", response_model=StudentRead)
def update_student(user_id: int, payload: StudentUpdate, db: Session = Depends(get_db)):
    student = StudentService.get_by_user_id(db, user_id)
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return StudentService.update_profile(db, student, payload)

@router.put("/{student_id}/interests")
def update_student_interests(student_id: int, interests: List[str], db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    student.interests = json.dumps(interests)
    db.commit()
    db.refresh(student)
    
    return {
        "student_id": student_id,
        "interests": interests,
        "message": "Intereses actualizados exitosamente"
    }

@router.get("/{student_id}/history")
def get_student_history(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    stories = db.query(Story).filter(Story.alumno_id == student_id).all()
    
    return {
        "student_id": student_id,
        "total_stories": len(stories),
        "stories": [
            {
                "id": s.id,
                "title": s.title,
                "topic": s.topic,
                "created_at": s.created_at.isoformat(),
                "word_count": len(s.content.split()) if s.content else 0
            }
            for s in stories
        ],
        "stats": {
            "total_points": student.total_points,
            "current_level": student.current_level
        }
    }

@router.get("/{student_id}/ranking")
def get_student_ranking(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    enrollment = db.query(Enrollment).filter(Enrollment.student_id == student_id).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="Estudiante no está asociado a ningún salón")
    
    all_enrollments = db.query(Enrollment).filter(
        Enrollment.teacher_id == enrollment.teacher_id
    ).all()
    
    student_ids = [e.student_id for e in all_enrollments]
    students = db.query(Student).filter(Student.id.in_(student_ids)).all()
    
    ranking = sorted(
        [
            {
                "student_id": s.id,
                "student_name": s.user.fullname if s.user else "Estudiante",
                "total_points": s.total_points,
                "current_level": s.current_level
            }
            for s in students
        ],
        key=lambda x: x["total_points"],
        reverse=True
    )
    
    for i, entry in enumerate(ranking):
        entry["position"] = i + 1
        entry["is_current_student"] = entry["student_id"] == student_id
    
    return {
        "student_id": student_id,
        "ranking": ranking,
        "total_students": len(ranking)
    }

@router.post("/join-class")
def join_class_with_code(classroom_code: str, student_id: int, db: Session = Depends(get_db)):
    from app.models.models import Teacher
    
    teacher = db.query(Teacher).filter(Teacher.classroom_code == classroom_code.upper()).first()
    
    if not teacher:
        raise HTTPException(status_code=404, detail="Código de clase inválido o no encontrado")
    
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.teacher_id == teacher.id,
        Enrollment.student_id == student_id
    ).first()
    
    if existing_enrollment:
        return {
            "message": "Ya estás inscrito en esta clase",
            "teacher_name": teacher.user.fullname if teacher.user else "Profesor"
        }
    
    new_enrollment = Enrollment(teacher_id=teacher.id, student_id=student_id)
    db.add(new_enrollment)
    db.commit()
    
    return {
        "message": "Te has unido exitosamente a la clase",
        "teacher_name": teacher.user.fullname if teacher.user else "Profesor",
        "classroom_code": classroom_code
    }

@router.get("/{student_id}/export-pdf")
def export_student_history_pdf(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    stories = db.query(Story).filter(Story.alumno_id == student_id).all()
    
    return {
        "message": "Datos preparados para PDF",
        "student_name": student.user.fullname if student.user else "Estudiante",
        "total_stories": len(stories),
        "total_points": student.total_points,
        "current_level": student.current_level,
        "stories_summary": [
            {
                "title": s.title,
                "date": s.created_at.isoformat(),
                "topic": s.topic
            }
            for s in stories
        ]
    }