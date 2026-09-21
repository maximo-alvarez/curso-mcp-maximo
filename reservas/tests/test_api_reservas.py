import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture(scope="module")
def test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_error_no_controlado_devuelve_500_sin_stacktrace(client):
    # Definir temporalmente una ruta que lanza una excepción imprevista
    @app.get("/test-unhandled-exception-internal")
    def trigger_error():
        raise RuntimeError("Fallo critico interno y secreto de infraestructura")

    response = client.get("/test-unhandled-exception-internal")

    assert response.status_code == 500
    assert response.json() == {"detail": "Error interno del servidor"}
    # Verificar que el mensaje secreto de la excepción no se filtra al cliente
    assert "Fallo critico" not in response.text


def test_registrar_usuario(client):
    response = client.post(
        "/usuarios/",
        json={"email": "nuevo_usuario@example.com", "password": "PasswordSegura123!"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["email"] == "nuevo_usuario@example.com"
    # Verificar que la contraseña no se expone jamás en la respuesta
    assert "password" not in data
    assert "hashed_password" not in data


def test_registrar_usuario_email_duplicado(client):
    payload = {"email": "duplicado@example.com", "password": "PasswordSegura123!"}
    res1 = client.post("/usuarios/", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/usuarios/", json=payload)
    assert res2.status_code == 400
    assert res2.json() == {"detail": "El email ya está registrado"}


def test_login_exitoso(client):
    client.post(
        "/usuarios/",
        json={"email": "login_user@example.com", "password": "Password123!"},
    )

    response = client.post(
        "/usuarios/token",
        data={"username": "login_user@example.com", "password": "Password123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_credenciales_invalidas(client):
    client.post(
        "/usuarios/",
        json={"email": "valid_user@example.com", "password": "CorrectPassword123!"},
    )

    # 1. Contraseña incorrecta
    res1 = client.post(
        "/usuarios/token",
        data={"username": "valid_user@example.com", "password": "WrongPassword!"},
    )
    assert res1.status_code == 401
    assert res1.json() == {"detail": "Credenciales inválidas"}

    # 2. Usuario inexistente
    res2 = client.post(
        "/usuarios/token",
        data={"username": "no_existe@example.com", "password": "AnyPassword!"},
    )
    assert res2.status_code == 401
    assert res2.json() == {"detail": "Credenciales inválidas"}


def test_crear_reserva_con_repo_falso(client):
    from app.dependencies import get_current_user, get_reservas_repo
    from app.models.usuario import Usuario

    usuario_autenticado = Usuario(id=10, email="tester@example.com", hashed_password="pwd")

    class RepositorioReservasFalsoAPI:
        def __init__(self):
            self.reservas = []

        def buscar_solapamiento(self, db, fecha, hora_inicio, hora_fin):
            return False

        def guardar(self, db, usuario_id, fecha, hora_inicio, hora_fin):
            return {
                "id": 101,
                "usuario_id": usuario_id,
                "fecha": fecha,
                "hora_inicio": hora_inicio,
                "hora_fin": hora_fin,
                "estado": "ACTIVA",
            }

    repo_falso = RepositorioReservasFalsoAPI()

    app.dependency_overrides[get_current_user] = lambda: usuario_autenticado
    app.dependency_overrides[get_reservas_repo] = lambda: repo_falso

    try:
        response = client.post(
            "/reservas/",
            json={
                "fecha": "2099-10-15",
                "hora_inicio": "10:00",
                "hora_fin": "12:00",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 101
        assert data["usuario_id"] == 10
        assert data["fecha"] == "2099-10-15"
        assert data["hora_inicio"] == "10:00"
        assert data["hora_fin"] == "12:00"
        assert data["estado"] == "ACTIVA"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_reservas_repo, None)


def test_crear_reserva_sin_token_devuelve_401(client):
    """Caso de Error 3: Petición a endpoint protegido sin token Bearer."""
    response = client.post(
        "/reservas/",
        json={
            "fecha": "2099-10-15",
            "hora_inicio": "10:00",
            "hora_fin": "12:00",
        },
    )
    assert response.status_code == 401


def test_listar_reservas_paginadas(client):
    # 1. Registrar usuario y obtener token
    email = "listar_api@example.com"
    client.post("/usuarios/", json={"email": email, "password": "Password123!"})
    token_res = client.post("/usuarios/token", data={"username": email, "password": "Password123!"})
    token = token_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Crear 3 reservas
    for i in range(3):
        client.post(
            "/reservas/",
            json={
                "fecha": f"2099-12-0{i+1}",
                "hora_inicio": "10:00",
                "hora_fin": "11:00",
            },
            headers=headers,
        )

    # 3. Listar todas con skip=0, limit=10
    res_todas = client.get("/reservas/?skip=0&limit=10", headers=headers)
    assert res_todas.status_code == 200
    data = res_todas.json()
    assert len(data) == 3
    assert all(r["estado"] == "ACTIVA" for r in data)

    # 4. Paginación con skip=1, limit=1
    res_pag = client.get("/reservas/?skip=1&limit=1", headers=headers)
    assert res_pag.status_code == 200
    assert len(res_pag.json()) == 1

    # 5. Validación de parámetros inválidos (skip negativo -> 422)
    res_invalida = client.get("/reservas/?skip=-1", headers=headers)
    assert res_invalida.status_code == 422


def test_listar_reservas_sin_token_devuelve_401(client):
    """Caso de Error 3: Consulta de reservas sin token de autenticación."""
    response = client.get("/reservas/")
    assert response.status_code == 401


def test_cancelar_reserva_exitosa(client):
    email = "cancelar_ok@example.com"
    client.post("/usuarios/", json={"email": email, "password": "Password123!"})
    token_res = client.post("/usuarios/token", data={"username": email, "password": "Password123!"})
    token = token_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post(
        "/reservas/",
        json={"fecha": "2099-12-20", "hora_inicio": "10:00", "hora_fin": "11:00"},
        headers=headers,
    )
    assert create_res.status_code == 201
    reserva_id = create_res.json()["id"]

    del_res = client.delete(f"/reservas/{reserva_id}", headers=headers)
    assert del_res.status_code == 204

    # Verificar que aparece en el listado con estado CANCELADA (soft delete)
    list_res = client.get("/reservas/", headers=headers)
    assert list_res.status_code == 200
    reserva_cancelada = next(r for r in list_res.json() if r["id"] == reserva_id)
    assert reserva_cancelada["estado"] == "CANCELADA"


def test_cancelar_reserva_ajena_devuelve_403(client):
    """Caso de Error 4: Intento de cancelar una reserva perteneciente a otro usuario."""
    # Usuario A
    email_a = "user_a_del@example.com"
    client.post("/usuarios/", json={"email": email_a, "password": "Password123!"})
    token_a = client.post("/usuarios/token", data={"username": email_a, "password": "Password123!"}).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Usuario B
    email_b = "user_b_del@example.com"
    client.post("/usuarios/", json={"email": email_b, "password": "Password123!"})
    token_b = client.post("/usuarios/token", data={"username": email_b, "password": "Password123!"}).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Usuario A crea reserva
    create_res = client.post(
        "/reservas/",
        json={"fecha": "2099-12-21", "hora_inicio": "14:00", "hora_fin": "15:00"},
        headers=headers_a,
    )
    reserva_id = create_res.json()["id"]

    # Usuario B intenta cancelarla -> 403
    del_res = client.delete(f"/reservas/{reserva_id}", headers=headers_b)
    assert del_res.status_code == 403
    assert "permisos" in del_res.json()["detail"].lower() or "no autorizado" in del_res.json()["detail"].lower()


def test_cancelar_reserva_inexistente_devuelve_404(client):
    """Caso de Error 5: Intento de cancelar una reserva inexistente."""
    email = "user_nonexistent_del@example.com"
    client.post("/usuarios/", json={"email": email, "password": "Password123!"})
    token = client.post("/usuarios/token", data={"username": email, "password": "Password123!"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    del_res = client.delete("/reservas/999999", headers=headers)
    assert del_res.status_code == 404
    assert del_res.json()["detail"] == "La reserva no existe"


def test_cancelar_reserva_sin_token_devuelve_401(client):
    """Caso de Error 3: Intento de cancelación sin token de autenticación."""
    response = client.delete("/reservas/1")
    assert response.status_code == 401



