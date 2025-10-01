from app.db.crud import CRUDRepository
from app.models.models import User, Student, Teacher, Story, Record, Enrollment
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import and_

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

    def get_by_student_and_teacher(self, db: Session, student_id: int, teacher_id: int) -> Optional[Enrollment]:
        return (
            db.query(Enrollment)
            .filter(
                Enrollment.student_id == student_id,
                Enrollment.teacher_id == teacher_id
            )
            .first()
        )

    def get_students_for_teacher(self, db: Session, teacher_id: int):
        from app.models.models import Student, User, Enrollment

        q = (
            db.query(
                Student.id.label('student_id'),
                User.fullname.label('fullname'),
                User.email.label('email'),
                User.activo.label('activo'),
                Student.current_grade,
                Student.interests,
                Student.current_level,
                Student.total_points,
                Student.last_updated_date,
                Enrollment.id.label('enrollment_id')
            )
            .join(User, Student.user_id == User.id)
            .outerjoin(
                Enrollment,
                and_(
                    Enrollment.student_id == Student.id,
                    Enrollment.teacher_id == teacher_id
                )
            )
            .all()
        )

        print("🔎 teacher_id recibido:", teacher_id)
        print("📋 Resultado crudo de q:")
        for row in q:
            print(dict(row._mapping))  # imprime como diccionario

        enrollments = db.query(Enrollment).all()
        print("📋 Todos los enrollments:")
        for e in enrollments:
            print(f"id={e.id}, student_id={e.student_id}, teacher_id={e.teacher_id}")

        result = []
        for row in q:
            result.append({
                "id": row.student_id,
                "fullname": row.fullname,
                "email": row.email,
                "activo": row.activo,
                "current_grade": row.current_grade,
                "interests": row.interests,
                "current_level": row.current_level,
                "total_points": row.total_points,
                "last_updated_date": row.last_updated_date,
                "matriculado": row.enrollment_id is not None
            })
        return result
