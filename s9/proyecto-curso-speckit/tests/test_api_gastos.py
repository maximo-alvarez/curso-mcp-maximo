import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.dependencies import get_current_user, get_gastos_repo
from app.models.usuario import Usuario
from tests.test_gastos import RepositorioFalso

USUARIO_DE_PRUEBA = Usuario(id=1, email="test@ejemplo.com", hashed_password="no-importa")


@pytest.fixture(scope="module")
def test_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="module")
def client(test_engine):
    SessionTest = sessionmaker(bind=test_engine)

    def override_get_db():
        db = SessionTest()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: USUARIO_DE_PRUEBA
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_error_no_controlado_devuelve_500_sin_stacktrace(client):
    class RepositorioRoto:
        def total_por_categoria(self, db, usuario_id, categoria):
            raise RuntimeError("la base de datos no responde")

        def guardar(self, *args, **kwargs):
            raise RuntimeError("la base de datos no responde")

    app.dependency_overrides[get_gastos_repo] = lambda: RepositorioRoto()

    response = client.post(
        "/gastos/", json={"descripcion": "Falla", "monto": 10.0, "categoria": "comida"}
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Error interno del servidor"}


def test_registrar_usuario(client):
    response = client.post("/usuarios/", json={"email": "nuevo_usuario@test.com", "password": "password123"})
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "nuevo_usuario@test.com"
    assert "password" not in data
    assert "hashed_password" not in data
    assert "id" in data


def test_registrar_usuario_email_duplicado(client):
    response = client.post("/usuarios/", json={"email": "nuevo_usuario@test.com", "password": "password123"})
    assert response.status_code == 400
    assert "ya está registrado" in response.json()["detail"]


def test_login_exitoso(client):
    response = client.post("/usuarios/token", data={"username": "nuevo_usuario@test.com", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_credenciales_invalidas(client):
    response = client.post("/usuarios/token", data={"username": "nuevo_usuario@test.com", "password": "password_incorrecto"})
    assert response.status_code == 401
    assert "detail" in response.json()


def test_crear_gasto_con_repo_falso(client):
    app.dependency_overrides[get_gastos_repo] = lambda: RepositorioFalso()

    response = client.post(
        "/gastos/", json={"descripcion": "Almuerzo", "monto": 12.50, "categoria": "comida"}
    )

    assert response.status_code == 201
    assert response.json()["descripcion"] == "Almuerzo"
    assert response.json()["monto"] == 12.50
    assert response.json()["categoria"] == "comida"


def test_crear_gasto_sin_token_devuelve_401(client):
    override = app.dependency_overrides.pop(get_current_user, None)
    try:
        response = client.post(
            "/gastos/", json={"descripcion": "Almuerzo", "monto": 12.50, "categoria": "comida"}
        )
        assert response.status_code == 401
    finally:
        if override:
            app.dependency_overrides[get_current_user] = override


def test_listar_gastos_con_paginacion(client):
    repo = RepositorioFalso()
    repo.guardar(None, USUARIO_DE_PRUEBA.id, "Gasto 1", 10.0, "comida")
    repo.guardar(None, USUARIO_DE_PRUEBA.id, "Gasto 2", 20.0, "transporte")
    app.dependency_overrides[get_gastos_repo] = lambda: repo

    response = client.get("/gastos/?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_listar_gastos_sin_token_devuelve_401(client):
    override = app.dependency_overrides.pop(get_current_user, None)
    try:
        response = client.get("/gastos/")
        assert response.status_code == 401
    finally:
        if override:
            app.dependency_overrides[get_current_user] = override


def test_listar_gastos_usuario_id_ajeno_ignorado(client):
    repo = RepositorioFalso()
    # Gastos de nuestro usuario (id=1)
    repo.guardar(None, USUARIO_DE_PRUEBA.id, "Gasto Propio", 10.0, "comida")
    # Gasto de otro usuario (id=999)
    repo.guardar(None, 999, "Gasto Ajeno", 500.0, "otros")
    app.dependency_overrides[get_gastos_repo] = lambda: repo

    # Enviar query param fraudulento con usuario_id=999
    response = client.get("/gastos/?usuario_id=999")
    assert response.status_code == 200
    data = response.json()
    # Debe devolver SOLO el gasto propio, nunca el ajeno
    assert len(data) == 1
    assert data[0]["descripcion"] == "Gasto Propio"
