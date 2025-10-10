import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

@pytest.fixture
def create_teacher(client):
    """Crea un usuario tipo teacher y retorna su payload de respuesta"""
    def _create_teacher(fullname="Profesor Uno", email="teacher@example.com"):
        response = client.post("/api/v1/auth/register", json={
            "fullname": fullname,
            "email": email,
            "password": "password123",
            "tipo": "teacher",
            "teacher_profile": {
                "current_school": "Colegio Central",
                "alma_mater": "UNI",
                "degree_level": "Licenciatura",
                "major": "Matemáticas"
            }
        })
        assert response.status_code == 200
        return response.json()
    return _create_teacher


def test_get_teacher_success(create_teacher):
    teacher = create_teacher()
    teacher_id = teacher["teacher_profile"]["id"]

    response = client.get(f"/api/v1/teachers/{teacher_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == teacher_id
    assert data["current_school"] == "Colegio Central"


def test_get_teacher_not_found():
    response = client.get("/api/v1/teachers/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Profesor no encontrado"


def test_update_teacher_success(create_teacher):
    teacher = create_teacher(email="update_teacher@example.com")
    teacher_id = teacher["teacher_profile"]["id"]

    response = client.put(f"/api/v1/teachers/{teacher_id}", json={
        "current_school": "Colegio Renovado",
        "alma_mater": "PUCP",
        "degree_level": "Maestría",
        "major": "Física"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["current_school"] == "Colegio Renovado"
    assert data["alma_mater"] == "PUCP"


def test_update_teacher_not_found():
    response = client.put("/api/v1/teachers/99999", json={
        "current_school": "No existe"
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Profesor no encontrado"
