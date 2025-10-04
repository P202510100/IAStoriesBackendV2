from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.repositories import UserRepository, StudentRepository, TeacherRepository
from app.models.models import User
from app.schemas.user import UserUpdate

user_repo = UserRepository()
student_repo = StudentRepository()
teacher_repo = TeacherRepository()

class UserService:
    @staticmethod
    def update_user(db: Session, user_id: int, payload: UserUpdate) -> User:
        # Buscar usuario
        user = user_repo.get(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Actualizar datos del User
        user_data = payload.model_dump(
            exclude_unset=True,
            exclude={"student_profile", "teacher_profile"}
        )
        updated_user = user_repo.update(db, user, user_data)

        # Si es estudiante y viene payload para actualizar
        if payload.student_profile and user.student_profile:
            student_repo.update(
                db,
                user.student_profile,
                payload.student_profile.model_dump(exclude_unset=True)
            )

        # Si es docente y viene payload para actualizar
        if payload.teacher_profile and user.teacher_profile:
            teacher_repo.update(
                db,
                user.teacher_profile,
                payload.teacher_profile.model_dump(exclude_unset=True)
            )

        return updated_user