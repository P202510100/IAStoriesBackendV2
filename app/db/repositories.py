from app.db.crud import CRUDRepository
from app.models.models import User, Student, Teacher, Story, Record, Enrollment
from sqlalchemy.orm import Session
from typing import Optional

class UserRepository(CRUDRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

class StudentRepository(CRUDRepository[Student]):
    def __init__(self):
        super().__init__(Student)

    def get_by_user_id(self, db: Session, user_id: int) -> Optional[Student]:
        return db.query(Student).filter(Student.user_id == user_id).first()

class TeacherRepository(CRUDRepository[Teacher]):
    def __init__(self):
        super().__init__(Teacher)

    def get_by_user_id(self, db: Session, user_id: int) -> Optional[Teacher]:
        return db.query(Teacher).filter(Teacher.user_id == user_id).first()

class StoryRepository(CRUDRepository[Story]):
    def __init__(self):
        super().__init__(Story)

class RecordRepository(CRUDRepository[Record]):
    def __init__(self):
        super().__init__(Record)

class EnrollmentRepository(CRUDRepository[Enrollment]):
    def __init__(self):
        super().__init__(Enrollment)
