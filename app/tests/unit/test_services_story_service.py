import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock
from app.services.story_service import StoryService


# ---------- Caso: create_story ----------
def test_create_story_calls_repo(monkeypatch):
    fake_db = MagicMock()
    fake_story_repo = MagicMock()
    monkeypatch.setattr("app.services.story_service.story_repo", fake_story_repo)

    fake_story_repo.create.return_value = {"id": 1, "title": "Test Story"}
    data = {"title": "Test Story", "content": "contenido"}

    result = StoryService.create_story(fake_db, data)

    assert result == {"id": 1, "title": "Test Story"}
    fake_story_repo.create.assert_called_once_with(fake_db, data)


# ---------- Caso: generate_story alumno no encontrado ----------
def test_generate_story_student_not_found(monkeypatch):
    fake_db = MagicMock()
    fake_student_repo = MagicMock()
    monkeypatch.setattr("app.services.story_service.student_repo", fake_student_repo)
    fake_student_repo.get_by_user_id.return_value = None

    from app.schemas.story import StoryGenerateRequest
    request = StoryGenerateRequest(
        user_id=1, nombre="Juan", edad=10, elementos="mapa", topic="aventura"
    )

    with pytest.raises(ValueError) as excinfo:
        StoryService.generate_story(fake_db, request)

    assert "Alumno no encontrado" in str(excinfo.value)


# ---------- Caso: generate_story flujo completo ----------
def test_generate_story_success(monkeypatch):
    fake_db = MagicMock()

    # Mock student_repo
    fake_student_repo = MagicMock()
    monkeypatch.setattr("app.services.story_service.student_repo", fake_student_repo)

    class DummyStudent:
        id = 123
        current_grade = "5to"
    fake_student_repo.get_by_user_id.return_value = DummyStudent()

    # Mock story_repo
    fake_story_repo = MagicMock()
    monkeypatch.setattr("app.services.story_service.story_repo", fake_story_repo)

    class DummyStory:
        id = 99
        title = "Historia generada"
        content = "contenido"
        topic = "aventura"
        question_answer = []
        story_metadata = {}
        characters = []
        student_id = 123
        image_b64 = None
        created_at = datetime.now(timezone.utc)
    fake_story_repo.create.return_value = DummyStory()

    # Mock generador de IA
    fake_ai = MagicMock()
    fake_ai.return_value = {
        "title": "Historia generada",
        "content": "contenido",
        "questions": [{"q": "pregunta", "options": ["a","b"], "answer": 0}],
        "story_metadata": {"grado": "5to"},
        "characters": ["Juan"],
        "image_b64": "b64data"
    }
    monkeypatch.setattr("app.services.story_service.generar_historia_preguntas_imagen", fake_ai)

    # Mock RecordService
    fake_record_service = MagicMock()
    fake_record = MagicMock()
    fake_record.id = 777
    fake_record_service.create_record_for_student.return_value = fake_record
    monkeypatch.setattr("app.services.story_service.RecordService", fake_record_service)

    from app.schemas.story import StoryGenerateRequest
    request = StoryGenerateRequest(
        user_id=1, nombre="Juan", edad=10, elementos="mapa", topic="aventura"
    )

    result = StoryService.generate_story(fake_db, request)

    # Validaciones
    assert result.title == "Historia generada"
    assert result.record_id == 777
    fake_ai.assert_called_once()
    fake_story_repo.create.assert_called_once()
    fake_record_service.create_record_for_student.assert_called_once()


# ---------- list_stories ----------
def test_list_stories(monkeypatch):
    fake_db = MagicMock()
    fake_story_repo = MagicMock()
    monkeypatch.setattr("app.services.story_service.story_repo", fake_story_repo)

    fake_story_repo.list.return_value = [{"id": 1, "title": "T1"}]

    result = StoryService.list_stories(fake_db, skip=0, limit=10)
    assert result == [{"id": 1, "title": "T1"}]
    fake_story_repo.list.assert_called_once_with(fake_db, skip=0, limit=10)


# ---------- list_stories_by_student ----------
def test_list_stories_by_student(monkeypatch):
    fake_db = MagicMock()
    fake_story_repo = MagicMock()
    monkeypatch.setattr("app.services.story_service.story_repo", fake_story_repo)

    fake_story_repo.list_by_student.return_value = [{"id": 2, "title": "T2"}]

    result = StoryService.list_stories_by_student(fake_db, student_id=5, skip=0, limit=10)
    assert result == [{"id": 2, "title": "T2"}]
    fake_story_repo.list_by_student.assert_called_once_with(fake_db, 5, skip=0, limit=10)
