import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def create_test_user():
    """Crea un usuario student para pruebas."""
    payload = {
        "fullname": "Test User",
        "email": "test_auth@example.com",
        "password": "password123",
        "tipo": "student"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200
    return response.json()


def test_register_user_success():
    """Debe registrar correctamente un usuario nuevo."""
    payload = {
        "fullname": "Nuevo Usuario",
        "email": "new_user@example.com",
        "password": "newpassword",
        "tipo": "teacher"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["tipo"] == "teacher"


def test_register_duplicate_email(create_test_user):
    """Debe devolver 400 si el email ya está registrado."""
    payload = {
        "fullname": "Test User",
        "email": "test_auth@example.com",
        "password": "password123",
        "tipo": "student"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "ya registrado" in response.json()["detail"]


def test_login_success(create_test_user):
    """Debe permitir el login y devolver token + datos del usuario."""
    payload = {"username": "test_auth@example.com", "password": "password123"}
    response = client.post("/api/v1/auth/login", data=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test_auth@example.com"


def test_login_invalid_credentials():
    """Debe rechazar credenciales incorrectas."""
    payload = {"username": "noexiste@example.com", "password": "wrong"}
    response = client.post("/api/v1/auth/login", data=payload)
    assert response.status_code == 401
    assert "Credenciales inválidas" in response.text


def test_verify_email(create_test_user):
    """Debe confirmar si el email existe."""
    response = client.post("/api/v1/auth/verify-email", json={"email": "test_auth@example.com"})
    assert response.status_code == 200
    assert response.json() == {"exists": True}


def test_verify_email_not_found():
    """Debe retornar 404 si el email no existe."""
    response = client.post("/api/v1/auth/verify-email", json={"email": "noexiste@example.com"})
    assert response.status_code == 404
    assert "No existe una cuenta" in response.text


def test_reset_password(create_test_user):
    """Debe permitir resetear la contraseña olvidada."""
    response = client.post("/api/v1/auth/reset-password", json={
        "email": "test_auth@example.com",
        "new_password": "newpass123"
    })
    assert response.status_code == 200
    assert "actualizada" in response.json()["message"]

    # Ahora podemos hacer login con la nueva contraseña
    login_resp = client.post("/api/v1/auth/login", data={
        "username": "test_auth@example.com",
        "password": "newpass123"
    })
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()


def test_change_password_flow(create_test_user):
    """Debe permitir cambiar contraseña si current_password es válida."""
    user = create_test_user

    # Login para obtener token
    login_resp = client.post("/api/v1/auth/login", data={
        "username": user["email"],
        "password": "password123"
    })
    token = login_resp.json()["access_token"]

    # Cambiar contraseña con el endpoint
    change_resp = client.post("/api/v1/auth/change-password", json={
        "user_id": user["id"],
        "current_password": "password123",
        "new_password": "nueva_segura_456"
    })
    assert change_resp.status_code == 200
    assert "actualizada" in change_resp.json()["message"]

    # Login con la nueva contraseña
    new_login = client.post("/api/v1/auth/login", data={
        "username": user["email"],
        "password": "nueva_segura_456"
    })
    assert new_login.status_code == 200


def test_change_password_wrong_current(create_test_user):
    """Debe rechazar si la contraseña actual es incorrecta."""
    user = create_test_user
    resp = client.post("/api/v1/auth/change-password", json={
        "user_id": user["id"],
        "current_password": "incorrecta",
        "new_password": "nueva_123"
    })
    assert resp.status_code == 400
    assert "incorrecta" in resp.text
