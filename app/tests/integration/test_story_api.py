import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

@pytest.fixture
def create_student_user():
    # Crear usuario tipo student
    user_resp = client.post("/api/v1/auth/register", json={
        "fullname": "Alumno Test",
        "email": "student_story@example.com",
        "password": "password123",
        "tipo": "student"
    })
    assert user_resp.status_code == 200
    user = user_resp.json()

    # Crear perfil student
    student_resp = client.post("/api/v1/students/", json={
        "user_id": user["id"],
        "birth_date": None,
        "current_grade": "5to",
        "interests": "aventuras, ciencia"
    })
    assert student_resp.status_code == 200
    student = student_resp.json()

    return user, student


def test_generate_story(create_student_user, monkeypatch):
    user, student = create_student_user

    # 🔹 Fake AI generator (mockeamos la llamada a OpenAI/IA)
    def fake_ai(**kwargs):
        return {
            "title": "Historia de prueba IA",
            "content": "Un cuento generado por IA.",
            "questions": [
                {"question": "¿Qué hizo el dragón?", "options": ["A", "B", "C", "D"], "answer": 0}
            ],
            "story_metadata": {"nivel": "test"},
            "characters": ["Dragón", "Príncipe"],
            "image_b64": "fake_b64_image"
        }

    monkeypatch.setattr("app.services.story_service.generar_historia_preguntas_imagen", fake_ai)

    # 🔹 Llamamos al endpoint /stories/generate
    resp = client.post("/api/v1/stories/generate", json={
        "user_id": user["id"],
        "nombre": "Alumno",
        "edad": 10,
        "elementos": "dragón, castillo",
        "topic": "aventura"
    })
    assert resp.status_code == 200
    story = resp.json()

    # 🔹 Validaciones
    assert story["title"] == "Historia de prueba IA"
    assert story["topic"] == "aventura"
    assert "record_id" in story
    assert story["record_id"] is not None
    assert story["characters"] == ["Dragón", "Príncipe"]


def test_list_stories(create_student_user, monkeypatch):
    user, student = create_student_user

    # Mock de IA igual al anterior
    monkeypatch.setattr(
        "app.services.story_service.generar_historia_preguntas_imagen",
        lambda **kwargs: {
            "title": "Historia para listar",
            "content": "Contenido fake",
            "questions": [],
            "story_metadata": {},
            "characters": ["Héroe"],
            "image_b64": "fakeimg"
        }
    )

    # Generamos una historia primero
    client.post("/api/v1/stories/generate", json={
        "user_id": user["id"],
        "nombre": "Alumno",
        "edad": 12,
        "elementos": "espada, bosque",
        "topic": "fantasía"
    })

    # Listamos historias
    list_resp = client.get("/api/v1/stories/")
    assert list_resp.status_code == 200
    stories = list_resp.json()

    assert len(stories) > 0
    assert any(st["title"] == "Historia para listar" for st in stories)
