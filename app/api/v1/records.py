from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List

from app.db.database import get_db
from app.services.record_service import RecordService
from app.schemas.record import RecordCreate, RecordRead, RecordUpdate
from app.models.models import Record
from app.schemas.answer import AnswerCreate, AnswerRead

router = APIRouter()

@router.post("/", response_model=RecordRead)
def create_record(user_id: int, payload: RecordCreate, db: Session = Depends(get_db)):
    try:
        return RecordService.create_record_for_student(db, user_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{record_id}", response_model=RecordRead)
def update_record(record_id: int, payload: RecordUpdate, db: Session = Depends(get_db)):
    try:
        return RecordService.update_record(db, record_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/student/{student_id}", response_model=list[RecordRead])
def get_student_records(student_id: int, db: Session = Depends(get_db)):
    records = (
        db.query(Record)
        .options(joinedload(Record.story))
        .filter(Record.student_id == student_id)
        .all()
    )

    return records

@router.post("/{record_id}/answers", response_model=AnswerRead)
def save_answer(record_id: int, payload: AnswerCreate, db: Session = Depends(get_db)):
    try:
        return RecordService.save_answer(
            db=db,
            record_id=record_id,
            question_index=payload.question_index,
            response=payload.response,
            is_correct=payload.is_correct
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{record_id}", response_model=RecordRead)
def get_record_detail(record_id: int, db: Session = Depends(get_db)):
    record = RecordService.get_record_with_answers(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@router.post("/{record_id}/save-progress")
def save_progress(record_id: int, payload: List[AnswerCreate], db: Session = Depends(get_db)):
    try:
        saved = RecordService.save_progress_bulk(db, record_id, payload)
        return {"status": "ok", "answers_saved": len(saved)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{record_id}/restart", response_model=RecordRead)
def restart_exam(record_id: int, db: Session = Depends(get_db)):
    try:
        return RecordService.restart_exam(db, record_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))