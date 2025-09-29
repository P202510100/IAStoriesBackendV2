from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repositories import TeacherRepository
from app.schemas.teacher import TeacherRead, TeacherUpdate

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
