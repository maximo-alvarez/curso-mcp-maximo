import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.reserva import Reserva


@pytest.fixture
def integration_env():
    """Configura una base de datos SQLite en memoria aislada para tests de integración reales."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSession()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, raise_server_exceptions=False) as client:
        # 1. Crear un usuario real mediante la API
        client.post(
            "/usuarios/",
            json={"email": "integracion@example.com", "password": "PasswordSegura123!"},
        )
        # 2. Obtener un token JWT legítimo
        token_res = client.post(
            "/usuarios/token",
            data={"username": "integracion@example.com", "password": "PasswordSegura123!"},
        )
        token = token_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        yield {
            "client": client,
            "headers": headers,
            "db": db,
        }

    app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_crear_reserva_integracion(integration_env):
    client = integration_env["client"]
    headers = integration_env["headers"]
    db = integration_env["db"]

    payload = {
        "fecha": "2099-11-20",
        "hora_inicio": "10:00",
        "hora_fin": "12:00",
    }
    response = client.post("/reservas/", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["fecha"] == "2099-11-20"
    assert data["hora_inicio"] == "10:00"
    assert data["hora_fin"] == "12:00"
    assert data["estado"] == "ACTIVA"

    # Verificar persistencia real en la base de datos SQLite
    reserva_db = db.query(Reserva).filter(Reserva.id == data["id"]).first()
    assert reserva_db is not None
    assert reserva_db.fecha == "2099-11-20"
    assert reserva_db.estado == "ACTIVA"


def test_solapamiento_bloqueado_integracion(integration_env):
    """Caso de Error 1 integrado: Dos reservas en el mismo intervalo horario son bloqueadas."""
    client = integration_env["client"]
    headers = integration_env["headers"]
    db = integration_env["db"]

    # 1. Crear primera reserva
    base_reserva = {
        "fecha": "2099-11-20",
        "hora_inicio": "14:00",
        "hora_fin": "16:00",
    }
    res1 = client.post("/reservas/", json=base_reserva, headers=headers)
    assert res1.status_code == 201

    # 2. Intentar crear reserva que se solapa (15:00 a 17:00)
    solapada = {
        "fecha": "2099-11-20",
        "hora_inicio": "15:00",
        "hora_fin": "17:00",
    }
    res2 = client.post("/reservas/", json=solapada, headers=headers)
    assert res2.status_code == 400
    assert res2.json() == {
        "detail": "El horario solicitado se solapa con una reserva existente"
    }

    # 3. Comprobar que en la base de datos sólo persiste la primera reserva
    total = db.query(Reserva).filter(Reserva.fecha == "2099-11-20").count()
    assert total == 1


def test_reservas_contiguas_permitidas_integracion(integration_env):
    """Verifica que intervalos contiguos ([10:00, 12:00) y [12:00, 14:00)) no colisionan."""
    client = integration_env["client"]
    headers = integration_env["headers"]
    db = integration_env["db"]

    # 1. Crear reserva A: 10:00 a 12:00
    res1 = client.post(
        "/reservas/",
        json={"fecha": "2099-11-21", "hora_inicio": "10:00", "hora_fin": "12:00"},
        headers=headers,
    )
    assert res1.status_code == 201

    # 2. Crear reserva contigua posterior B: 12:00 a 14:00
    res2 = client.post(
        "/reservas/",
        json={"fecha": "2099-11-21", "hora_inicio": "12:00", "hora_fin": "14:00"},
        headers=headers,
    )
    assert res2.status_code == 201

    # 3. Crear reserva contigua anterior C: 08:00 a 10:00
    res3 = client.post(
        "/reservas/",
        json={"fecha": "2099-11-21", "hora_inicio": "08:00", "hora_fin": "10:00"},
        headers=headers,
    )
    assert res3.status_code == 201

    # Verificar que las 3 reservas existen y están activas en SQLite
    reservas = db.query(Reserva).filter(Reserva.fecha == "2099-11-21").all()
    assert len(reservas) == 3
    assert all(r.estado == "ACTIVA" for r in reservas)


def test_aislamiento_entre_usuarios_reservas_integracion(integration_env):
    """US3 Integración: Garantiza 0% de fuga de información entre usuarios y funcionamiento de paginación."""
    client = integration_env["client"]

    # 1. Crear Usuario A y obtener su token
    client.post("/usuarios/", json={"email": "usuario_a@example.com", "password": "PasswordA123!"})
    token_a = client.post(
        "/usuarios/token",
        data={"username": "usuario_a@example.com", "password": "PasswordA123!"},
    ).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Crear Usuario B y obtener su token
    client.post("/usuarios/", json={"email": "usuario_b@example.com", "password": "PasswordB123!"})
    token_b = client.post(
        "/usuarios/token",
        data={"username": "usuario_b@example.com", "password": "PasswordB123!"},
    ).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. Crear 3 reservas para Usuario A
    for i in range(3):
        res = client.post(
            "/reservas/",
            json={"fecha": f"2099-12-1{i}", "hora_inicio": "09:00", "hora_fin": "10:00"},
            headers=headers_a,
        )
        assert res.status_code == 201

    # 4. Crear 2 reservas para Usuario B
    for i in range(2):
        res = client.post(
            "/reservas/",
            json={"fecha": f"2099-12-2{i}", "hora_inicio": "14:00", "hora_fin": "15:00"},
            headers=headers_b,
        )
        assert res.status_code == 201

    # 5. Listar reservas de Usuario A
    res_a = client.get("/reservas/?skip=0&limit=10", headers=headers_a)
    assert res_a.status_code == 200
    data_a = res_a.json()
    assert len(data_a) == 3
    uid_a = data_a[0]["usuario_id"]
    assert all(r["usuario_id"] == uid_a for r in data_a)

    # 6. Listar reservas de Usuario B
    res_b = client.get("/reservas/?skip=0&limit=10", headers=headers_b)
    assert res_b.status_code == 200
    data_b = res_b.json()
    assert len(data_b) == 2
    uid_b = data_b[0]["usuario_id"]
    assert uid_b != uid_a
    assert all(r["usuario_id"] == uid_b for r in data_b)

    # 7. Aislamiento cruzado estricto: cero intersección de IDs de reservas entre A y B
    ids_a = {r["id"] for r in data_a}
    ids_b = {r["id"] for r in data_b}
    assert ids_a.isdisjoint(ids_b)

    # 8. Paginación en Usuario A
    res_a_pag = client.get("/reservas/?skip=1&limit=1", headers=headers_a)
    assert res_a_pag.status_code == 200
    data_a_pag = res_a_pag.json()
    assert len(data_a_pag) == 1
    assert data_a_pag[0]["id"] == data_a[1]["id"]


def test_cancelacion_soft_delete_y_reutilizacion_horario_integracion(integration_env):
    """US4 Integración: Verifica cancelación soft-delete, preservación de datos en BD y liberación inmediata del horario."""
    client = integration_env["client"]
    headers_a = integration_env["headers"]
    db = integration_env["db"]

    # 1. Crear Usuario B para verificar la posterior reutilización del horario por otro usuario
    client.post("/usuarios/", json={"email": "usuario_b_reuso@example.com", "password": "PasswordB123!"})
    token_b = client.post(
        "/usuarios/token",
        data={"username": "usuario_b_reuso@example.com", "password": "PasswordB123!"},
    ).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 2. Usuario A crea una reserva en 2099-11-25 de 10:00 a 12:00
    horario = {"fecha": "2099-11-25", "hora_inicio": "10:00", "hora_fin": "12:00"}
    res_crear = client.post("/reservas/", json=horario, headers=headers_a)
    assert res_crear.status_code == 201
    reserva_id_a = res_crear.json()["id"]

    # 3. Usuario B intenta reservar el mismo horario solapado -> Rechazado con 400
    res_solapada = client.post("/reservas/", json=horario, headers=headers_b)
    assert res_solapada.status_code == 400

    # 4. Usuario A cancela su reserva vía DELETE /reservas/{id} -> 204 No Content
    res_cancelar = client.delete(f"/reservas/{reserva_id_a}", headers=headers_a)
    assert res_cancelar.status_code == 204

    # 5. Comprobar soft delete directo en la base de datos (no se eliminó la fila física)
    reserva_en_db = db.query(Reserva).filter(Reserva.id == reserva_id_a).first()
    assert reserva_en_db is not None
    assert reserva_en_db.estado == "CANCELADA"

    # 6. Usuario B ahora puede reservar exactamente el mismo horario liberado
    res_reuso = client.post("/reservas/", json=horario, headers=headers_b)
    assert res_reuso.status_code == 201
    reserva_id_b = res_reuso.json()["id"]
    assert reserva_id_b != reserva_id_a
    assert res_reuso.json()["estado"] == "ACTIVA"

    # 7. Comprobar que en la base de datos existen ambos registros para la misma fecha
    reservas_db = db.query(Reserva).filter(Reserva.fecha == "2099-11-25").all()
    assert len(reservas_db) == 2
    estados = {r.id: r.estado for r in reservas_db}
    assert estados[reserva_id_a] == "CANCELADA"
    assert estados[reserva_id_b] == "ACTIVA"


