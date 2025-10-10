import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_db
from sqlalchemy.orm import Session

client = TestClient(app)


@pytest.fixture
def create_user():
    """Crea un usuario de prueba usando el endpoint /auth/register."""
    def _create_user(fullname="Test User", email="user@example.com", tipo="student"):
        response = client.post("/api/v1/auth/register", json={
            "fullname": fullname,
            "email": email,
            "password": "password123",
            "tipo": tipo
        })
        assert response.status_code == 200
        return response.json()
    return _create_user


def test_list_users_returns_users(create_user):
    u1 = create_user("User One", "one@example.com")
    u2 = create_user("User Two", "two@example.com")

    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    # deberían estar los dos usuarios
    emails = [u["email"] for u in data]
    assert "one@example.com" in emails
    assert "two@example.com" in emails


def test_get_user_success(create_user):
    user = create_user("Test User", "getuser@example.com")
    response = client.get(f"/api/v1/users/{user['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user["id"]
    assert data["email"] == "getuser@example.com"
    assert data["fullname"] == "Test User"


def test_get_user_not_found():
    response = client.get("/api/v1/users/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Usuario no encontrado"


def test_update_user_success(create_user):
    user = create_user("Old Name", "update@example.com")
    response = client.put(f"/api/v1/users/{user['id']}", json={
        "activo": 1,
        "fullname": "New Name",
        "email": "update@example.com"  # 👈 obligatorio porque UserUpdate espera email opcional pero validado
    })
    print("🔍 RESPONSE JSON 1:", response.json())

    assert response.status_code == 200
    data = response.json()
    assert data["fullname"] == "New Name"
    assert data["id"] == user["id"]


def test_update_user_not_found():
    response = client.put("/api/v1/users/99999", json={
        "activo": 1,
        "fullname": "Nobody",
        "email": "nobody@example.com"
    })
    print("🔍 RESPONSE JSON 2:", response.json())

    assert response.status_code == 404
    assert response.json()["detail"] == "Usuario no encontrado"
