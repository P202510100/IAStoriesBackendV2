from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.record_service import RecordService
from app.schemas.record import RecordCreate, RecordRead

router = APIRouter()

@router.post("/", response_model=RecordRead)
def create_record(user_id: int, payload: RecordCreate, db: Session = Depends(get_db)):
    try:
        return RecordService.create_record_for_student(db, user_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
