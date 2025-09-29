from sqlalchemy.orm import Session
from app.db.repositories import EnrollmentRepository, StudentRepository, TeacherRepository

enrollment_repo = EnrollmentRepository()
student_repo = StudentRepository()
teacher_repo = TeacherRepository()

class EnrollmentService:
    @staticmethod
    def enroll_student(db: Session, teacher_id: int, student_id: int):
        teacher = teacher_repo.get(db, teacher_id)
        student = student_repo.get(db, student_id)
        if not teacher or not student:
            raise ValueError("Teacher o Student no encontrado")
        return enrollment_repo.create(db, {
            "teacher_id": teacher.id,
            "student_id": student.id
        })
