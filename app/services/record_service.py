from sqlalchemy.orm import Session
from app.db.repositories import RecordRepository, StudentRepository, StoryRepository
from app.schemas.record import RecordCreate
from app.models.models import Record as RecordModel
from datetime import datetime

record_repo = RecordRepository()
student_repo = StudentRepository()
story_repo = StoryRepository()

class RecordService:
    @staticmethod
    def create_record_for_student(db: Session, user_id: int, payload: RecordCreate) -> RecordModel:
        student = student_repo.get_by_user_id(db, user_id)
        if not student:
            raise ValueError("Perfil de estudiante no encontrado")

        story = story_repo.get(db, payload.story_id)
        if not story:
            raise ValueError("Historia no encontrada")

        points = payload.points if payload.points is not None else payload.correct_answers

        record = record_repo.create(db, {
            "story_id": payload.story_id,
            "student_id": student.id,
            "points": points,
            "correct_answers": payload.correct_answers,
            "total_questions": payload.total_questions,
            "completed_at": datetime.utcnow()
        })

        # actualizar puntos del estudiante
        student_repo.update(db, student, {
            "total_points": student.total_points + points,
            "last_updated_date": datetime.utcnow()
        })

        return record
