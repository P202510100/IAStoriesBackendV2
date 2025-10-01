from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.services.student_service import StudentService
from app.schemas.student import StudentRead, StudentUpdate

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

@router.get("/", response_model=List[StudentRead])
def list_students(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return StudentService.list_users(db, skip, limit)
