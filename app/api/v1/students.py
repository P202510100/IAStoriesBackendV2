from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.services.student_service import StudentService
from app.schemas.student import StudentRead, StudentUpdate, StudentDetail, StudentCreate

router = APIRouter()

@router.post("/", response_model=StudentRead)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    print("📥 Payload recibido en /students/:", payload.model_dump() if hasattr(payload, "dict") else payload)
    student = StudentService.create(db, payload)
    if not student:
        raise HTTPException(status_code=400, detail="No se pudo crear el estudiante")
    return student

@router.get("/by-user/{user_id}", response_model=StudentRead)
def get_student_by_user(user_id: int, db: Session = Depends(get_db)):
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

@router.get("/{student_id}", response_model=StudentDetail)
def get_student_detail(student_id: int, db: Session = Depends(get_db)):
    try:
        return StudentService.get_student_detail(db, student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{student_id}/interests")
def update_student_interests(student_id: int, interests: list[str], db: Session = Depends(get_db)):
    updated = StudentService.update_interests(db, student_id, interests)
    if not updated:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return {"message": "Intereses actualizados correctamente", "interests": updated.interests}