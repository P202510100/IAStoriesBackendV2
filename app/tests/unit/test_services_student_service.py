import pytest
from unittest.mock import MagicMock
from datetime import datetime
from app.services.student_service import StudentService


def test_get_by_user_id_returns_student(monkeypatch):
    fake_db = MagicMock()
    fake_student_repo = MagicMock()
    monkeypatch.setattr("app.services.student_service.student_repo", fake_student_repo)

    class DummyStudent:
        id = 1
        user_id = 10

    fake_student_repo.get_by_user_id.return_value = DummyStudent()

    result = StudentService.get_by_user_id(fake_db, user_id=10)

    assert result.id == 1
    fake_student_repo.get_by_user_id.assert_called_once_with(fake_db, 10)


def test_update_profile_updates_fields(monkeypatch):
    fake_db = MagicMock()
    fake_student_repo = MagicMock()
    monkeypatch.setattr("app.services.student_service.student_repo", fake_student_repo)

    class DummyStudent:
        id = 1
        current_grade = "4to"

    updated_student = DummyStudent()
    updated_student.current_grade = "5to"

    fake_student_repo.update.return_value = updated_student

    from app.schemas.student import StudentUpdate
    payload = StudentUpdate(current_grade="5to")

    result = StudentService.update_profile(fake_db, DummyStudent(), payload)

    assert result.current_grade == "5to"

    args, kwargs = fake_student_repo.update.call_args
    data_arg = args[2]
    assert "last_updated_date" in data_arg
    assert data_arg["current_grade"] == "5to"

def test_list_users_returns_students(monkeypatch):
    fake_db = MagicMock()
    fake_student_repo = MagicMock()
    monkeypatch.setattr("app.services.student_service.student_repo", fake_student_repo)

    class DummyStudent:
        id = 1

    fake_student_repo.list.return_value = [DummyStudent(), DummyStudent()]

    result = StudentService.list_users(fake_db, skip=0, limit=10)

    assert len(result) == 2
    fake_student_repo.list.assert_called_once_with(fake_db, skip=0, limit=10)


def test_get_student_detail_success(monkeypatch):
    fake_db = MagicMock()
    fake_student_repo = MagicMock()
    monkeypatch.setattr("app.services.student_service.student_repo", fake_student_repo)

    class DummyStudent:
        id = 1
        user_id = 10

    fake_student_repo.get_with_user.return_value = DummyStudent()

    result = StudentService.get_student_detail(fake_db, 1)

    assert result.id == 1
    fake_student_repo.get_with_user.assert_called_once_with(fake_db, 1)


def test_get_student_detail_not_found(monkeypatch):
    fake_db = MagicMock()
    fake_student_repo = MagicMock()
    monkeypatch.setattr("app.services.student_service.student_repo", fake_student_repo)

    fake_student_repo.get_with_user.return_value = None

    with pytest.raises(ValueError) as exc:
        StudentService.get_student_detail(fake_db, 1)

    assert "Estudiante no encontrado" in str(exc.value)
