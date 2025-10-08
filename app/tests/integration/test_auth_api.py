def test_register_and_login(client):
    # Registrar un usuario
    response = client.post("/api/v1/auth/register", json={
        "fullname": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "tipo": "student"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"

    # Login con credenciales correctas
    response = client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token
