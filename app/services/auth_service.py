from sqlalchemy.orm import Session
from app.db.repositories import UserRepository, StudentRepository, TeacherRepository
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.models import User as UserModel, UserType
from typing import Optional
from datetime import timedelta

user_repo = UserRepository()
student_repo = StudentRepository()
teacher_repo = TeacherRepository()

class AuthService:
    @staticmethod
    def register_user(db: Session, user_in: UserCreate) -> UserModel:
        # verificar duplicado
        existing = user_repo.get_by_email(db, str(user_in.email))
        if existing:
            raise ValueError("Email ya registrado")

        hashed_pw = get_password_hash(user_in.password)

        user = user_repo.create(db, {
            "fullname": user_in.fullname,
            "email": user_in.email,
            "password": hashed_pw,
            "tipo": user_in.tipo
        })

        # crear perfil según tipo
        if user.tipo == UserType.student and user_in.student_profile:
            student_repo.create(
                db,
                {
                    "user_id": user.id,
                    **user_in.student_profile.dict()
                }
            )
        elif user.tipo == UserType.teacher and user_in.teacher_profile:
            teacher_repo.create(
                db,
                {
                    "user_id": user.id,
                    **user_in.teacher_profile.dict()
                }
            )

        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[UserModel]:
        user = user_repo.get_by_email(db, str(email))
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    @staticmethod
    def create_token_for_user(user: UserModel, expires_minutes: int = 60) -> str:
        return create_access_token(
            subject=str(user.id),
            expires_delta=timedelta(minutes=expires_minutes)
        )
