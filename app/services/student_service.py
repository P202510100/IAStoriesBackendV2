from typing import List

from sqlalchemy.orm import Session
from app.db.repositories import StudentRepository
from app.schemas.student import StudentUpdate
from app.models.models import Student as StudentModel
from datetime import datetime

student_repo = StudentRepository()

class StudentService:
    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> StudentModel | None:
        return student_repo.get_by_user_id(db, user_id)

    @staticmethod
    def update_profile(db: Session, student: StudentModel, payload: StudentUpdate) -> StudentModel:
        data = payload.dict(exclude_unset=True)
        data["last_updated_date"] = datetime.utcnow()
        return student_repo.update(db, student, data)

    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 50) -> List[StudentModel]:
        return student_repo.list(db, skip=skip, limit=limit)
