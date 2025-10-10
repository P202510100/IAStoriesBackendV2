import pytest
from unittest.mock import MagicMock
from datetime import timedelta
from jose import jwt

from app.services.auth_service import AuthService
from app.core import security
from app.models.models import UserType

# ---------- register_user ----------
def test_register_user_creates_user_and_profile(monkeypatch):
    fake_db = MagicMock()

    # Simula repositorios
    fake_user_repo = MagicMock()
    fake_student_repo = MagicMock()
    fake_teacher_repo = MagicMock()

    monkeypatch.setattr("app.services.auth_service.user_repo", fake_user_repo)
    monkeypatch.setattr("app.services.auth_service.student_repo", fake_student_repo)
    monkeypatch.setattr("app.services.auth_service.teacher_repo", fake_teacher_repo)

    # Simula que no existe el usuario
    fake_user_repo.get_by_email.return_value = None

    # Usuario de prueba
    class DummyUser:
        id = 1
        email = "test@test.com"
        password = "hashed"
        tipo = UserType.student

    fake_user_repo.create.return_value = DummyUser()

    # UserCreate simulado
    class DummyProfile:
        def model_dump(self, **kwargs):
            return {"grade": "5to"}

    class DummyUserIn:
        fullname = "Test User"
        email = "test@test.com"
        password = "1234567"
        tipo = UserType.student
        student_profile = DummyProfile()
        teacher_profile = None

    user = AuthService.register_user(fake_db, DummyUserIn)

    assert user.email == "test@test.com"
    fake_user_repo.get_by_email.assert_called_once()
    fake_user_repo.create.assert_called_once()
    fake_student_repo.create.assert_called_once_with(fake_db, {"user_id": 1, "grade": "5to"})
    fake_teacher_repo.create.assert_not_called()

def test_register_user_duplicate_email(monkeypatch):
    fake_db = MagicMock()

    fake_user_repo = MagicMock()
    monkeypatch.setattr("app.services.auth_service.user_repo", fake_user_repo)
    fake_user_repo.get_by_email.return_value = {"id": 1, "email": "dup@test.com"}

    from app.schemas.user import UserCreate
    dummy_in = UserCreate(fullname="Dup", email="dup@test.com", password="123456789", tipo=UserType.student)

    with pytest.raises(ValueError):
        AuthService.register_user(fake_db, dummy_in)

# ---------- authenticate_user ----------
def test_authenticate_user_ok(monkeypatch):
    fake_db = MagicMock()

    fake_user_repo = MagicMock()
    monkeypatch.setattr("app.services.auth_service.user_repo", fake_user_repo)

    class DummyUser:
        id = 1
        email = "x@test.com"
        password = security.get_password_hash("secret")

    fake_user_repo.get_by_email.return_value = DummyUser()

    user = AuthService.authenticate_user(fake_db, "x@test.com", "secret")
    assert user.email == "x@test.com"

def test_authenticate_user_wrong_password(monkeypatch):
    fake_db = MagicMock()
    fake_user_repo = MagicMock()
    monkeypatch.setattr("app.services.auth_service.user_repo", fake_user_repo)

    class DummyUser:
        id = 1
        email = "x@test.com"
        password = security.get_password_hash("secret")

    fake_user_repo.get_by_email.return_value = DummyUser()

    user = AuthService.authenticate_user(fake_db, "x@test.com", "badpass")
    assert user is None

def test_authenticate_user_not_found(monkeypatch):
    fake_db = MagicMock()
    fake_user_repo = MagicMock()
    monkeypatch.setattr("app.services.auth_service.user_repo", fake_user_repo)
    fake_user_repo.get_by_email.return_value = None

    user = AuthService.authenticate_user(fake_db, "none@test.com", "secret")
    assert user is None

# ---------- create_token_for_user ----------
def test_create_token_for_user_decodable(monkeypatch):
    class DummyUser:
        id = 42
        email = "tokentest@test.com"
        password = "hashed"
        tipo = UserType.teacher

    token = AuthService.create_token_for_user(DummyUser(), expires_minutes=5)

    payload = security.decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "42"
