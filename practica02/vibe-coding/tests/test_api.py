import pytest
from fastapi.testclient import TestClient

from vibe_coding.api import app
from vibe_coding.validators import limpiar_usuarios

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    limpiar_usuarios()
    yield
    limpiar_usuarios()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "vibe-coding-api"

def test_validate_password_valid():
    response = client.post(
        "/api/v1/validate/password",
        json={"password": "Password123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valida"] is True
    assert len(data["errores"]) == 0

def test_validate_password_invalid():
    response = client.post(
        "/api/v1/validate/password",
        json={"password": "12345"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valida"] is False
    assert len(data["errores"]) > 0

def test_validate_email_valid():
    response = client.post(
        "/api/v1/validate/email",
        json={"email": "ana@correo.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valida"] is True
    assert len(data["errores"]) == 0

def test_validate_email_invalid():
    response = client.post(
        "/api/v1/validate/email",
        json={"email": "ana@"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valida"] is False
    assert len(data["errores"]) > 0

def test_create_user_standard_success():
    response = client.post(
        "/api/v1/users",
        json={
            "email": "ana@correo.com",
            "password": "Password123!",
            "es_admin": False
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["mensaje"] == "Usuario registrado exitosamente."
    assert data["usuario"]["email"] == "ana@correo.com"
    assert data["usuario"]["es_admin"] is False
    assert data["usuario"]["has_password"] is True

def test_create_user_standard_weak_password_fails():
    response = client.post(
        "/api/v1/users",
        json={
            "email": "carlos@empresa.org",
            "password": "12345",
            "es_admin": False
        }
    )
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "errores" in detail
    assert len(detail["errores"]) > 0

def test_create_user_admin_weak_password_allowed():
    response = client.post(
        "/api/v1/users",
        json={
            "email": "admin@empresa.org",
            "password": "123",
            "es_admin": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["usuario"]["email"] == "admin@empresa.org"
    assert data["usuario"]["es_admin"] is True

def test_create_user_admin_empty_password_allowed():
    response = client.post(
        "/api/v1/users",
        json={
            "email": "superadmin@empresa.org",
            "password": "",
            "es_admin": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["usuario"]["email"] == "superadmin@empresa.org"
    assert data["usuario"]["has_password"] is False

def test_create_duplicate_user_fails():
    # Registrar primer usuario
    client.post(
        "/api/v1/users",
        json={"email": "usuario@test.com", "password": "Password123!", "es_admin": False}
    )
    # Intentar registrar mismo correo
    response = client.post(
        "/api/v1/users",
        json={"email": "usuario@test.com", "password": "Password123!", "es_admin": False}
    )
    assert response.status_code == 400
    assert "El correo electrónico ya está registrado." in response.json()["detail"]["errores"]

def test_list_users():
    client.post(
        "/api/v1/users",
        json={"email": "user1@test.com", "password": "Password123!", "es_admin": False}
    )
    client.post(
        "/api/v1/users",
        json={"email": "admin@test.com", "password": "123", "es_admin": True}
    )

    response = client.get("/api/v1/users")
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 2
    assert users[0]["email"] == "user1@test.com"
    assert users[1]["email"] == "admin@test.com"
