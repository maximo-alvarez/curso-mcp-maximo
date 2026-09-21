from datetime import timedelta
import pytest
import jwt

from app.mcp.auth import JWTTokenVerifier
from app.security import ALGORITHM, crear_access_token


@pytest.mark.anyio
async def test_jwt_token_verifier_mcp():
    verifier = JWTTokenVerifier()

    # 1. Token válido con claim sub
    token_valido = crear_access_token({"sub": "usuario_123", "email": "test@example.com"})
    access_token = await verifier.verify_token(token_valido)
    assert access_token is not None
    assert access_token.token == token_valido
    assert access_token.subject == "usuario_123"
    assert access_token.client_id == "usuario_123"
    assert access_token.claims["email"] == "test@example.com"
    assert access_token.expires_at is not None

    # 2. Token sin claim sub
    token_sin_sub = crear_access_token({"email": "test@example.com"})
    res_sin_sub = await verifier.verify_token(token_sin_sub)
    assert res_sin_sub is None

    # 3. Token con sub vacío
    token_sub_vacio = crear_access_token({"sub": ""})
    res_sub_vacio = await verifier.verify_token(token_sub_vacio)
    assert res_sub_vacio is None

    # 4. Token expirado
    token_expirado = crear_access_token({"sub": "usuario_123"}, expires_delta=timedelta(minutes=-10))
    res_expirado = await verifier.verify_token(token_expirado)
    assert res_expirado is None

    # 5. Token con firma inválida (otra clave secreta)
    token_clave_invalida = jwt.encode(
        {"sub": "usuario_123"},
        "otra_clave_secreta_con_longitud_suficiente_para_evitar_warnings_32b",
        algorithm=ALGORITHM,
    )
    res_clave_invalida = await verifier.verify_token(token_clave_invalida)
    assert res_clave_invalida is None


    # 6. Token malformado
    res_malformado = await verifier.verify_token("cadena.invalida.malformada")
    assert res_malformado is None


def test_mcp_server_setup():
    from app.config import settings
    from app.mcp.auth import JWTTokenVerifier
    from app.mcp.server import mcp_server

    assert mcp_server.name == "reservas-mcp"
    assert mcp_server.settings.streamable_http_path == "/"
    assert isinstance(mcp_server._token_verifier, JWTTokenVerifier)
    assert mcp_server.settings.auth is not None
    assert str(mcp_server.settings.auth.issuer_url).rstrip("/") == settings.MCP_ISSUER_URL.rstrip("/")
    assert str(mcp_server.settings.auth.resource_server_url).rstrip("/") == settings.MCP_RESOURCE_URL.rstrip("/")
    assert mcp_server.settings.auth.validate_token_resource is False


@pytest.fixture
def mcp_test_db(monkeypatch):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool
    from app.database import Base
    import app.models.reserva  # noqa: F401
    import app.models.usuario  # noqa: F401

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_test_session():
        return TestingSession()

    monkeypatch.setattr("app.mcp.tools.reservas._obtener_db", get_test_session)
    yield TestingSession
    Base.metadata.drop_all(bind=engine)


def test_mcp_crear_reserva_tool(mcp_test_db):
    """Verifica creación de reserva exitosa y manejo de errores estructurados en MCP."""
    from app.mcp.tools.reservas import crear_reserva

    # 1. Creación exitosa
    res = crear_reserva(fecha="2099-10-15", hora_inicio="10:00", hora_fin="12:00")
    assert "id" in res
    assert res["fecha"] == "2099-10-15"
    assert res["hora_inicio"] == "10:00"
    assert res["hora_fin"] == "12:00"
    assert res["estado"] == "ACTIVA"

    # 2. Error por solapamiento
    res_solapada = crear_reserva(fecha="2099-10-15", hora_inicio="11:00", hora_fin="13:00")
    assert res_solapada == {"error": "El horario solicitado se solapa con una reserva existente"}

    # 3. Error por hora inválida
    res_hora_invalida = crear_reserva(fecha="2099-10-15", hora_inicio="14:00", hora_fin="12:00")
    assert res_hora_invalida == {"error": "La hora de fin debe ser posterior a la hora de inicio"}

    # 4. Error por fecha pasada
    res_fecha_pasada = crear_reserva(fecha="2020-01-01", hora_inicio="10:00", hora_fin="12:00")
    assert res_fecha_pasada == {"error": "No se pueden crear reservas en fechas pasadas"}


def test_mcp_listar_reservas_tool(mcp_test_db):
    """Verifica listado y paginación de reservas del usuario en MCP."""
    from app.mcp.tools.reservas import crear_reserva, listar_reservas

    crear_reserva(fecha="2099-11-01", hora_inicio="09:00", hora_fin="10:00")
    crear_reserva(fecha="2099-11-02", hora_inicio="10:00", hora_fin="11:00")

    lista = listar_reservas(skip=0, limit=10)
    assert isinstance(lista, list)
    assert len(lista) == 2
    assert all("id" in r and "estado" in r for r in lista)

    # Paginación
    pag = listar_reservas(skip=1, limit=1)
    assert len(pag) == 1
    assert pag[0]["fecha"] == "2099-11-02"


def test_mcp_cancelar_reserva_requiere_confirmacion(mcp_test_db):
    """Verifica confirmación en dos pasos: confirmacion=False no muta el estado de la reserva."""
    from app.mcp.tools.reservas import cancelar_reserva, crear_reserva, listar_reservas

    res = crear_reserva(fecha="2099-11-05", hora_inicio="09:00", hora_fin="10:00")
    reserva_id = res["id"]

    # Paso 1: Intento sin confirmación explícita
    resp_sin_conf = cancelar_reserva(reserva_id=reserva_id, confirmacion=False)
    assert resp_sin_conf["status"] == "confirmation_required"
    assert f"reserva #{reserva_id}" in resp_sin_conf["message"]
    assert "confirmacion=True" in resp_sin_conf["message"]

    # Comprobar que la reserva sigue ACTIVA
    lista = listar_reservas()
    encontrada = next(r for r in lista if r["id"] == reserva_id)
    assert encontrada["estado"] == "ACTIVA"


def test_mcp_cancelar_reserva_confirmada(mcp_test_db):
    """Verifica confirmación en dos pasos: confirmacion=True ejecuta el soft delete y valida permisos."""
    from mcp.server.auth.middleware.auth_context import AuthenticatedUser, auth_context_var
    from mcp.server.auth.provider import AccessToken
    from app.mcp.tools.reservas import cancelar_reserva, crear_reserva, listar_reservas

    # Usuario demo crea reserva
    res = crear_reserva(fecha="2099-11-10", hora_inicio="09:00", hora_fin="10:00")
    reserva_id = res["id"]

    # Usuario B intenta cancelarla con confirmación -> error 403 / no autorizado
    user_b = AuthenticatedUser(AccessToken(token="tok_b", client_id="user_b", scopes=[], subject="user_b@example.com"))
    tok_ctx = auth_context_var.set(user_b)
    try:
        resp_ajena = cancelar_reserva(reserva_id=reserva_id, confirmacion=True)
        assert "error" in resp_ajena
        assert "permisos" in resp_ajena["error"].lower() or "no autorizado" in resp_ajena["error"].lower()
    finally:
        auth_context_var.reset(tok_ctx)

    # Dueño original cancela con confirmacion=True -> éxito
    resp_ok = cancelar_reserva(reserva_id=reserva_id, confirmacion=True)
    assert resp_ok["status"] == "success"
    assert f"Reserva #{reserva_id} cancelada exitosamente" in resp_ok["message"]

    # Verificar transición de estado a CANCELADA
    lista = listar_reservas()
    cancelada = next(r for r in lista if r["id"] == reserva_id)
    assert cancelada["estado"] == "CANCELADA"

    # Intentar cancelar reserva inexistente con confirmacion=True -> error estructurado
    resp_inexistente = cancelar_reserva(reserva_id=99999, confirmacion=True)
    assert resp_inexistente == {"error": "La reserva no existe"}


def test_mcp_streamable_http_endpoint_mounted():
    """Verifica que el servidor MCP esté montado en /mcp con autenticación Bearer y lifespan activo."""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.security import crear_access_token

    token = crear_access_token({"sub": "mcp_tester@example.com"})

    with TestClient(app, base_url="http://127.0.0.1:8000") as client:
        # 1. Petición sin token -> 401 Unauthorized
        res_sin_token = client.get("/mcp/")
        assert res_sin_token.status_code == 401

        # 2. Petición con token válido -> Acceso procesado por el transporte MCP (no 401)
        res_con_token = client.get("/mcp/", headers={"Authorization": f"Bearer {token}"})
        assert res_con_token.status_code != 401


def test_vscode_mcp_config_json():
    """Verifica que .vscode/mcp.json exista, sea JSON válido y defina transporte dual (Art. VI.4)."""
    import json
    from pathlib import Path

    mcp_json_path = Path(__file__).parent.parent / ".vscode" / "mcp.json"
    assert mcp_json_path.exists()

    with open(mcp_json_path, encoding="utf-8") as f:
        config = json.load(f)

    assert "mcpServers" in config
    servers = config["mcpServers"]
    assert "reservas-streamable-http" in servers
    assert "reservas-stdio" in servers

    http_cfg = servers["reservas-streamable-http"]
    assert "/mcp" in http_cfg["url"]
    assert "Authorization" in http_cfg["headers"]

    stdio_cfg = servers["reservas-stdio"]
    assert stdio_cfg["command"] == "uv"
    assert "app.mcp.server" in stdio_cfg["args"]




