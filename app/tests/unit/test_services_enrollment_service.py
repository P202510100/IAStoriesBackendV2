import pytest
from unittest.mock import MagicMock
from app.services.enrollment_service import EnrollmentService


# ---------- enroll_student ----------
def test_enroll_student_teacher_or_student_not_found(monkeypatch):
    fake_db = MagicMock()

    fake_teacher_repo = MagicMock()
    fake_student_repo = MagicMock()
    monkeypatch.setattr("app.services.enrollment_service.teacher_repo", fake_teacher_repo)
    monkeypatch.setattr("app.services.enrollment_service.student_repo", fake_student_repo)

    fake_teacher_repo.get.return_value = None
    fake_student_repo.get.return_value = None

    with pytest.raises(ValueError) as exc:
        EnrollmentService.enroll_student(fake_db, teacher_id=1, student_id=2)
    assert "Teacher o Student no encontrado" in str(exc.value)


def test_enroll_student_already_exists(monkeypatch):
    fake_db = MagicMock()

    fake_teacher_repo = MagicMock()
    fake_student_repo = MagicMock()
    fake_enrollment_repo = MagicMock()

    monkeypatch.setattr("app.services.enrollment_service.teacher_repo", fake_teacher_repo)
    monkeypatch.setattr("app.services.enrollment_service.student_repo", fake_student_repo)
    monkeypatch.setattr("app.services.enrollment_service.enrollment_repo", fake_enrollment_repo)

    class DummyTeacher: id = 1
    class DummyStudent: id = 2

    fake_teacher_repo.get.return_value = DummyTeacher()
    fake_student_repo.get.return_value = DummyStudent()
    fake_enrollment_repo.get_by_student_and_teacher.return_value = {"id": 123}

    with pytest.raises(ValueError) as exc:
        EnrollmentService.enroll_student(fake_db, teacher_id=1, student_id=2)
    assert "ya está inscrito" in str(exc.value)


def test_enroll_student_success(monkeypatch):
    fake_db = MagicMock()

    fake_teacher_repo = MagicMock()
    fake_student_repo = MagicMock()
    fake_enrollment_repo = MagicMock()

    monkeypatch.setattr("app.services.enrollment_service.teacher_repo", fake_teacher_repo)
    monkeypatch.setattr("app.services.enrollment_service.student_repo", fake_student_repo)
    monkeypatch.setattr("app.services.enrollment_service.enrollment_repo", fake_enrollment_repo)

    class DummyTeacher: id = 1
    class DummyStudent: id = 2
    class DummyEnrollment: id = 999

    fake_teacher_repo.get.return_value = DummyTeacher()
    fake_student_repo.get.return_value = DummyStudent()
    fake_enrollment_repo.get_by_student_and_teacher.return_value = None
    fake_enrollment_repo.create.return_value = DummyEnrollment()

    result = EnrollmentService.enroll_student(fake_db, teacher_id=1, student_id=2)

    assert result.id == 999
    fake_enrollment_repo.create.assert_called_once()


# ---------- list_students_for_teacher ----------
def test_list_students_for_teacher(monkeypatch):
    fake_db = MagicMock()
    fake_enrollment_repo = MagicMock()
    monkeypatch.setattr("app.services.enrollment_service.enrollment_repo", fake_enrollment_repo)

    fake_enrollment_repo.get_students_for_teacher.return_value = [{"id": 1, "fullname": "Alumno"}]

    result = EnrollmentService.list_students_for_teacher(fake_db, teacher_id=5)

    assert result == [{"id": 1, "fullname": "Alumno"}]
    fake_enrollment_repo.get_students_for_teacher.assert_called_once_with(fake_db, 5)


# ---------- unenroll_student ----------
def test_unenroll_student_not_found(monkeypatch):
    fake_db = MagicMock()
    fake_teacher_repo = MagicMock()
    fake_student_repo = MagicMock()

    monkeypatch.setattr("app.services.enrollment_service.teacher_repo", fake_teacher_repo)
    monkeypatch.setattr("app.services.enrollment_service.student_repo", fake_student_repo)

    fake_teacher_repo.get.return_value = None
    fake_student_repo.get.return_value = None

    with pytest.raises(ValueError) as exc:
        EnrollmentService.unenroll_student(fake_db, teacher_id=1, student_id=2)
    assert "Teacher o Student no encontrado" in str(exc.value)


def test_unenroll_student_enrollment_not_found(monkeypatch):
    fake_db = MagicMock()
    fake_teacher_repo = MagicMock()
    fake_student_repo = MagicMock()
    fake_enrollment_repo = MagicMock()

    monkeypatch.setattr("app.services.enrollment_service.teacher_repo", fake_teacher_repo)
    monkeypatch.setattr("app.services.enrollment_service.student_repo", fake_student_repo)
    monkeypatch.setattr("app.services.enrollment_service.enrollment_repo", fake_enrollment_repo)

    class DummyTeacher: id = 1
    class DummyStudent: id = 2

    fake_teacher_repo.get.return_value = DummyTeacher()
    fake_student_repo.get.return_value = DummyStudent()
    fake_enrollment_repo.get_by_student_and_teacher.return_value = None

    with pytest.raises(ValueError) as exc:
        EnrollmentService.unenroll_student(fake_db, teacher_id=1, student_id=2)
    assert "no está inscrito" in str(exc.value)


def test_unenroll_student_success(monkeypatch):
    fake_db = MagicMock()
    fake_db.delete = MagicMock()
    fake_db.commit = MagicMock()

    fake_teacher_repo = MagicMock()
    fake_student_repo = MagicMock()
    fake_enrollment_repo = MagicMock()

    monkeypatch.setattr("app.services.enrollment_service.teacher_repo", fake_teacher_repo)
    monkeypatch.setattr("app.services.enrollment_service.student_repo", fake_student_repo)
    monkeypatch.setattr("app.services.enrollment_service.enrollment_repo", fake_enrollment_repo)

    class DummyTeacher: id = 1
    class DummyStudent: id = 2
    class DummyEnrollment: id = 10

    teacher = DummyTeacher()
    student = DummyStudent()
    enrollment = DummyEnrollment()

    fake_teacher_repo.get.return_value = teacher
    fake_student_repo.get.return_value = student
    fake_enrollment_repo.get_by_student_and_teacher.return_value = enrollment

    result = EnrollmentService.unenroll_student(fake_db, teacher_id=1, student_id=2)

    assert result["message"] == "Estudiante desmatriculado correctamente"
    fake_db.delete.assert_called_once_with(enrollment)
    fake_db.commit.assert_called_once()
