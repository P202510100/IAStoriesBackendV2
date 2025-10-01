from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.enrollment_service import EnrollmentService
from app.schemas.enrollment import EnrollmentCreate, EnrollmentRead

router = APIRouter()

@router.post("/", response_model=EnrollmentRead)
def enroll_student(payload: EnrollmentCreate, db: Session = Depends(get_db)):
    try:
        return EnrollmentService.enroll_student(db, payload.teacher_id, payload.student_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/teacher/{teacher_id}/students")
def get_students_for_teacher(teacher_id: int, db: Session = Depends(get_db)):
    return EnrollmentService.list_students_for_teacher(db, teacher_id)