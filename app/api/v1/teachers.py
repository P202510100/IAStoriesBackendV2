from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import secrets
import string

from app.db.database import get_db
from app.db.repositories import TeacherRepository
from app.schemas.teacher import TeacherRead, TeacherUpdate
from app.models.models import Teacher, Student, Story, Enrollment
from app.services.ai_services import GamificationService

router = APIRouter()
teacher_repo = TeacherRepository()

@router.get("/{teacher_id}", response_model=TeacherRead)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = teacher_repo.get(db, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return teacher

@router.put("/{teacher_id}", response_model=TeacherRead)
def update_teacher(teacher_id: int, payload: TeacherUpdate, db: Session = Depends(get_db)):
    teacher = teacher_repo.get(db, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return teacher_repo.update(db, teacher, payload.dict(exclude_unset=True))

@router.get("/{teacher_id}/students")
def get_teacher_students(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Docente no encontrado")
    
    enrollments = db.query(Enrollment).filter(Enrollment.teacher_id == teacher_id).all()
    
    students_data = []
    for enrollment in enrollments:
        student = db.query(Student).filter(Student.id == enrollment.student_id).first()
        if student:
            story_count = db.query(Story).filter(Story.alumno_id == student.id).count()
            
            students_data.append({
                "student_id": student.id,
                "name": student.user.fullname if student.user else "Estudiante",
                "email": student.user.email if student.user else "",
                "total_stories": story_count,
                "total_points": student.total_points,
                "current_level": student.current_level
            })
    
    return {
        "teacher_id": teacher_id,
        "total_students": len(students_data),
        "students": students_data
    }

@router.get("/{teacher_id}/classroom-ranking")
def get_classroom_ranking(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Docente no encontrado")
    
    enrollments = db.query(Enrollment).filter(Enrollment.teacher_id == teacher_id).all()
    student_ids = [e.student_id for e in enrollments]
    students = db.query(Student).filter(Student.id.in_(student_ids)).all()
    
    ranking_data = []
    for student in students:
        story_count = db.query(Story).filter(Story.alumno_id == student.id).count()
        level_info = GamificationService.calculate_level(student.total_points)
        
        ranking_data.append({
            "student_id": student.id,
            "name": student.user.fullname if student.user else "Estudiante",
            "total_points": student.total_points,
            "total_stories": story_count,
            "level": level_info["level"],
            "level_name": level_info["level_name"],
            "level_color": level_info["color"]
        })
    
    ranking_data.sort(key=lambda x: x["total_points"], reverse=True)
    
    for i, entry in enumerate(ranking_data):
        entry["position"] = i + 1
        if i == 0:
            entry["medal"] = "🥇"
        elif i == 1:
            entry["medal"] = "🥈"
        elif i == 2:
            entry["medal"] = "🥉"
        else:
            entry["medal"] = ""
    
    return {
        "teacher_id": teacher_id,
        "total_students": len(ranking_data),
        "ranking": ranking_data
    }

@router.get("/{teacher_id}/analytics")
def get_teacher_analytics(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Docente no encontrado")
    
    enrollments = db.query(Enrollment).filter(Enrollment.teacher_id == teacher_id).all()
    student_ids = [e.student_id for e in enrollments]
    students = db.query(Student).filter(Student.id.in_(student_ids)).all()
    
    total_students = len(students)
    total_stories = db.query(Story).filter(Story.alumno_id.in_(student_ids)).count()
    total_points = sum(s.total_points for s in students)
    avg_points = total_points / total_students if total_students > 0 else 0
    
    stories = db.query(Story).filter(Story.alumno_id.in_(student_ids)).all()
    theme_distribution = {}
    for story in stories:
        theme = story.topic or "otros"
        theme_distribution[theme] = theme_distribution.get(theme, 0) + 1
    
    top_students = sorted(students, key=lambda s: s.total_points, reverse=True)[:3]
    
    return {
        "teacher_id": teacher_id,
        "summary": {
            "total_students": total_students,
            "total_stories": total_stories,
            "total_points": total_points,
            "average_points": round(avg_points, 2),
            "average_stories_per_student": round(total_stories / total_students, 2) if total_students > 0 else 0
        },
        "theme_distribution": theme_distribution,
        "top_students": [
            {
                "name": s.user.fullname if s.user else "Estudiante",
                "points": s.total_points,
                "level": GamificationService.calculate_level(s.total_points)["level_name"]
            }
            for s in top_students
        ]
    }

@router.post("/{teacher_id}/generate-classroom-code")
def generate_classroom_code(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Docente no encontrado")
    
    def generate_code():
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    
    while True:
        code = generate_code()
        existing = db.query(Teacher).filter(Teacher.classroom_code == code).first()
        if not existing:
            break
    
    teacher.classroom_code = code
    db.commit()
    
    return {
        "teacher_id": teacher_id,
        "classroom_code": code,
        "message": "Código de clase generado exitosamente",
        "share_url": f"/join-class?code={code}"
    }

@router.delete("/{teacher_id}/students/{student_id}")
def unenroll_student(teacher_id: int, student_id: int, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Docente no encontrado")
    
    enrollment = db.query(Enrollment).filter(
        Enrollment.teacher_id == teacher_id,
        Enrollment.student_id == student_id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="Estudiante no está inscrito con este docente")
    
    db.delete(enrollment)
    db.commit()
    
    return {
        "message": "Estudiante desvinculado exitosamente",
        "teacher_id": teacher_id,
        "student_id": student_id
    }

@router.get("/{teacher_id}/export-report")
def export_teacher_report(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Docente no encontrado")
    
    enrollments = db.query(Enrollment).filter(Enrollment.teacher_id == teacher_id).all()
    student_ids = [e.student_id for e in enrollments]
    students = db.query(Student).filter(Student.id.in_(student_ids)).all()
    
    from datetime import datetime
    
    report_data = {
        "teacher_name": teacher.user.fullname if teacher.user else "Profesor",
        "report_date": datetime.now().isoformat(),
        "total_students": len(students),
        "students_detail": [
            {
                "name": s.user.fullname if s.user else "Estudiante",
                "total_stories": db.query(Story).filter(Story.alumno_id == s.id).count(),
                "total_points": s.total_points,
                "level": GamificationService.calculate_level(s.total_points)["level_name"]
            }
            for s in students
        ]
    }
    
    return {
        "message": "Datos preparados para reporte PDF",
        "report_data": report_data
    }