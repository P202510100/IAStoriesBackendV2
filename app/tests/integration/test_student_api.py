import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture
def create_student_user():
    def _create(fullname="Student User", email="student@example.com"):
        # Registramos un usuario tipo student
        response = client.post("/api/v1/auth/register", json={
            "fullname": fullname,
            "email": email,
            "password": "password123",
            "tipo": "student",
            "student_profile": {
                "current_grade": "4to",
                "interests": "math"
            }
        })
        assert response.status_code == 200
        return response.json()
    return _create


def test_get_student_by_user_success(create_student_user):
    user = create_student_user()
    response = client.get(f"/api/v1/students/by-user/{user['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user["id"]
    assert data["user"]["fullname"] == "Student User"


def test_get_student_by_user_not_found():
    response = client.get("/api/v1/students/by-user/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Estudiante no encontrado"


def test_update_student_success(create_student_user):
    user = create_student_user()
    response = client.put(f"/api/v1/students/{user['id']}", json={
        "current_grade": "5to",
        "interests": "science"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["current_grade"] == "5to"
    assert data["interests"] == "science"


def test_update_student_not_found():
    response = client.put("/api/v1/students/99999", json={
        "current_grade": "5to"
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Estudiante no encontrado"


def test_list_students_returns_students(create_student_user):
    create_student_user("Student 1", "s1@example.com")
    create_student_user("Student 2", "s2@example.com")
    response = client.get("/api/v1/students/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert "fullname" in data[0]["user"]


def test_get_student_detail_success(create_student_user):
    user = create_student_user()
    response = client.get(f"/api/v1/students/{user['student_profile']['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["id"] == user["id"]
    assert data["user"]["fullname"] == "Student User"


def test_get_student_detail_not_found():
    response = client.get("/api/v1/students/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Estudiante no encontrado"
