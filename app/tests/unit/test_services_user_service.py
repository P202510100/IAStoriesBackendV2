import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from app.services.user_service import UserService


def test_update_user_not_found(monkeypatch):
    fake_db = MagicMock()
    fake_user_repo = MagicMock()
    monkeypatch.setattr("app.services.user_service.user_repo", fake_user_repo)
    fake_user_repo.get.return_value = None

    from app.schemas.user import UserUpdate
    payload = UserUpdate(
        fullname="Nuevo Nombre",
        email="new@test.com",
        activo=True
    )

    with pytest.raises(HTTPException) as excinfo:
        UserService.update_user(fake_db, user_id=1, payload=payload)

    assert excinfo.value.status_code == 404
    assert "Usuario no encontrado" in excinfo.value.detail


def test_update_user_updates_basic_fields(monkeypatch):
    fake_db = MagicMock()
    fake_user_repo = MagicMock()
    fake_student_repo = MagicMock()
    fake_teacher_repo = MagicMock()

    monkeypatch.setattr("app.services.user_service.user_repo", fake_user_repo)
    monkeypatch.setattr("app.services.user_service.student_repo", fake_student_repo)
    monkeypatch.setattr("app.services.user_service.teacher_repo", fake_teacher_repo)

    class DummyUser:
        id = 1
        email = "old@test.com"
        fullname = "Old Name"
        student_profile = None
        teacher_profile = None

    updated_user = DummyUser()
    updated_user.fullname = "New Name"

    fake_user_repo.get.return_value = DummyUser()
    fake_user_repo.update.return_value = updated_user

    from app.schemas.user import UserUpdate
    payload = UserUpdate(
        fullname="New Name",
        email="old@test.com",
        activo=True
    )

    result = UserService.update_user(fake_db, user_id=1, payload=payload)

    assert result.fullname == "New Name"
    fake_user_repo.update.assert_called_once()


def test_update_user_updates_student_profile(monkeypatch):
    fake_db = MagicMock()
    fake_user_repo = MagicMock()
    fake_student_repo = MagicMock()

    monkeypatch.setattr("app.services.user_service.user_repo", fake_user_repo)
    monkeypatch.setattr("app.services.user_service.student_repo", fake_student_repo)

    class DummyStudentProfile:
        id = 99

    class DummyUser:
        id = 1
        fullname = "Student"
        student_profile = DummyStudentProfile()
        teacher_profile = None

    fake_user_repo.get.return_value = DummyUser()
    fake_user_repo.update.return_value = DummyUser()

    from app.schemas.user import UserUpdate
    from app.schemas.student import StudentUpdate
    payload = UserUpdate(
        fullname="Student",
        email="student@test.com",
        activo=True,
        student_profile=StudentUpdate(current_grade="5to")
    )

    UserService.update_user(fake_db, user_id=1, payload=payload)

    fake_student_repo.update.assert_called_once()


def test_update_user_updates_teacher_profile(monkeypatch):
    fake_db = MagicMock()
    fake_user_repo = MagicMock()
    fake_teacher_repo = MagicMock()

    monkeypatch.setattr("app.services.user_service.user_repo", fake_user_repo)
    monkeypatch.setattr("app.services.user_service.teacher_repo", fake_teacher_repo)

    class DummyTeacherProfile:
        id = 55

    class DummyUser:
        id = 2
        fullname = "Teacher"
        student_profile = None
        teacher_profile = DummyTeacherProfile()

    fake_user_repo.get.return_value = DummyUser()
    fake_user_repo.update.return_value = DummyUser()

    from app.schemas.user import UserUpdate
    from app.schemas.teacher import TeacherUpdate
    payload = UserUpdate(
        fullname="Teacher",
        email="teacher@test.com",
        activo=True,
        teacher_profile=TeacherUpdate(current_school="High School")
    )
    UserService.update_user(fake_db, user_id=2, payload=payload)

    fake_teacher_repo.update.assert_called_once()
