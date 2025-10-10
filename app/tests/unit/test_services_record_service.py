import pytest
from unittest.mock import MagicMock
from datetime import datetime
from app.services.record_service import RecordService


# ---------- create_record_for_student ----------
def test_create_record_student_not_found(monkeypatch):
    fake_db = MagicMock()
    fake_student_repo = MagicMock()
    monkeypatch.setattr("app.services.record_service.student_repo", fake_student_repo)
    fake_student_repo.get_by_user_id.return_value = None

    from app.schemas.record import RecordCreate
    payload = RecordCreate(story_id=1, correct_answers=0, total_questions=3, points=0)

    with pytest.raises(ValueError) as exc:
        RecordService.create_record_for_student(fake_db, user_id=1, payload=payload)
    assert "Perfil de estudiante" in str(exc.value)


def test_create_record_story_not_found(monkeypatch):
    fake_db = MagicMock()
    fake_student_repo = MagicMock()
    fake_story_repo = MagicMock()
    monkeypatch.setattr("app.services.record_service.student_repo", fake_student_repo)
    monkeypatch.setattr("app.services.record_service.story_repo", fake_story_repo)

    class DummyStudent: id = 10
    fake_student_repo.get_by_user_id.return_value = DummyStudent()
    fake_story_repo.get.return_value = None

    from app.schemas.record import RecordCreate
    payload = RecordCreate(story_id=1, correct_answers=0, total_questions=3, points=0)

    with pytest.raises(ValueError) as exc:
        RecordService.create_record_for_student(fake_db, user_id=1, payload=payload)
    assert "Historia no encontrada" in str(exc.value)


def test_create_record_success(monkeypatch):
    fake_db = MagicMock()

    fake_student_repo = MagicMock()
    fake_story_repo = MagicMock()
    fake_record_repo = MagicMock()

    monkeypatch.setattr("app.services.record_service.student_repo", fake_student_repo)
    monkeypatch.setattr("app.services.record_service.story_repo", fake_story_repo)
    monkeypatch.setattr("app.services.record_service.record_repo", fake_record_repo)

    class DummyStudent: id = 10
    class DummyStory: id = 99
    class DummyRecord: id = 123

    fake_student_repo.get_by_user_id.return_value = DummyStudent()
    fake_story_repo.get.return_value = DummyStory()
    fake_record_repo.create.return_value = DummyRecord()

    from app.schemas.record import RecordCreate
    payload = RecordCreate(story_id=99, correct_answers=2, total_questions=3, points=5)

    record = RecordService.create_record_for_student(fake_db, user_id=1, payload=payload)
    assert record.id == 123
    fake_record_repo.create.assert_called_once()


# ---------- update_record ----------
def test_update_record_not_found(monkeypatch):
    fake_db = MagicMock()
    fake_record_repo = MagicMock()
    monkeypatch.setattr("app.services.record_service.record_repo", fake_record_repo)
    fake_record_repo.get.return_value = None

    from app.schemas.record import RecordUpdate
    payload = RecordUpdate(status="IN_PROGRESS")

    with pytest.raises(ValueError):
        RecordService.update_record(fake_db, record_id=1, payload=payload)


def test_update_record_completed(monkeypatch):
    fake_db = MagicMock()

    fake_record_repo = MagicMock()
    fake_answer_repo = MagicMock()
    fake_student_repo = MagicMock()

    monkeypatch.setattr("app.services.record_service.record_repo", fake_record_repo)
    monkeypatch.setattr("app.services.record_service.answer_repo", fake_answer_repo)
    monkeypatch.setattr("app.services.record_service.student_repo", fake_student_repo)

    class DummyStory:
        question_answer = [{"q": "?", "options": ["a","b"], "answer": 0}]

    class DummyRecord:
        id = 1
        student_id = 5
        story = DummyStory()

    class DummyStudent:
        id = 5
        total_points = 10

    # Mock repos
    fake_record_repo.get.return_value = DummyRecord()
    fake_answer_repo.list_by_record.return_value = [MagicMock(is_correct=True)]
    fake_student_repo.get.return_value = DummyStudent()

    from app.schemas.record import RecordUpdate
    payload = RecordUpdate(status="COMPLETED")

    updated = MagicMock()
    fake_record_repo.update.return_value = updated

    result = RecordService.update_record(fake_db, record_id=1, payload=payload)

    assert result == updated
    fake_record_repo.update.assert_called_once()
    fake_student_repo.update.assert_called_once()


# ---------- save_answer ----------
def test_save_answer_new(monkeypatch):
    fake_db = MagicMock()

    fake_record_repo = MagicMock()
    fake_answer_repo = MagicMock()
    monkeypatch.setattr("app.services.record_service.record_repo", fake_record_repo)
    monkeypatch.setattr("app.services.record_service.answer_repo", fake_answer_repo)

    class DummyRecord: id = 1
    fake_record_repo.get.return_value = DummyRecord()
    fake_answer_repo.get_by_record_and_question.return_value = None

    fake_answer_repo.create.return_value = {"id": 10, "response": "A"}

    result = RecordService.save_answer(fake_db, 1, 0, "A", True)
    assert result["id"] == 10
    fake_answer_repo.create.assert_called_once()


def test_save_answer_update_existing(monkeypatch):
    fake_db = MagicMock()

    fake_record_repo = MagicMock()
    fake_answer_repo = MagicMock()
    monkeypatch.setattr("app.services.record_service.record_repo", fake_record_repo)
    monkeypatch.setattr("app.services.record_service.answer_repo", fake_answer_repo)

    class DummyRecord: id = 1
    class DummyAnswer: id = 10
    fake_record_repo.get.return_value = DummyRecord()
    fake_answer_repo.get_by_record_and_question.return_value = DummyAnswer()
    fake_answer_repo.update.return_value = {"id": 10, "response": "B"}

    result = RecordService.save_answer(fake_db, 1, 0, "B", False)
    assert result["response"] == "B"
    fake_answer_repo.update.assert_called_once()


# ---------- save_progress_bulk ----------
def test_save_progress_bulk(monkeypatch):
    fake_db = MagicMock()
    fake_db.commit = MagicMock()

    fake_record_repo = MagicMock()
    monkeypatch.setattr("app.services.record_service.record_repo", fake_record_repo)
    fake_record_repo.get.return_value = MagicMock()

    # Patch save_answer to a dummy function
    monkeypatch.setattr("app.services.record_service.RecordService.save_answer", lambda **kwargs: {"id": 1})

    from app.schemas.answer import AnswerCreate
    answers = [AnswerCreate(question_index=0, response="A", is_correct=True)]

    result = RecordService.save_progress_bulk(fake_db, record_id=1, answers=answers)
    assert result == [{"id": 1}]
    fake_db.commit.assert_called_once()
