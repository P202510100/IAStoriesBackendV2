from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import get_password_hash
from app.models.models import User
from app.db.database import get_db
from app.schemas.user import UserCreate, UserRead, EmailRequest, PasswordResetRequest
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/register", response_model=UserRead)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    try:
        user = AuthService.register_user(db, user_in)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    token = AuthService.create_token_for_user(user)
    db.refresh(user)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserRead.model_validate(user)
    }

@router.post("/verify-email")
def verify_email(request: EmailRequest, db: Session = Depends(get_db)):
    try:
        AuthService.verify_email(db, request.email)
        return {"exists": True}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/reset-password")
def reset_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    try:
        AuthService.reset_password(db, request.email, request.new_password)
        return {"message": "Contraseña actualizada correctamente"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

