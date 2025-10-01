from sqlalchemy.orm import Session
from app.db.repositories import EnrollmentRepository, StudentRepository, TeacherRepository

enrollment_repo = EnrollmentRepository()
student_repo = StudentRepository()
teacher_repo = TeacherRepository()

class EnrollmentService:
    @staticmethod
    def enroll_student(db: Session, teacher_id: int, student_id: int):
        # 1️⃣ Validar existencia de teacher y student
        teacher = teacher_repo.get(db, teacher_id)
        student = student_repo.get(db, student_id)

        print("📥 student_id recibido:", student_id)
        print("📥 teacher_id recibido:", teacher_id)

        if not teacher or not student:
            raise ValueError("Teacher o Student no encontrado")

        # 2️⃣ Validar duplicado (un mismo student no se puede inscribir con el mismo teacher 2 veces)
        existing = enrollment_repo.get_by_student_and_teacher(db, student_id, teacher_id)
        if existing:
            raise ValueError("El estudiante ya está inscrito con este docente")

        # 3️⃣ Crear la inscripción
        enrollment = enrollment_repo.create(db, {
            "teacher_id": teacher.id,
            "student_id": student.id
        })

        return enrollment

    @staticmethod
    def list_students_for_teacher(db: Session, teacher_id: int):
        return enrollment_repo.get_students_for_teacher(db, teacher_id)

