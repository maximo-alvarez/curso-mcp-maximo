import pytest
from app.mcp.auth import JWTTokenVerifier
from app.security import crear_access_token


@pytest.mark.anyio
async def test_jwt_token_verifier_valido_e_invalido():
    verifier = JWTTokenVerifier()

    token_valido = crear_access_token({"sub": "mcp_user@test.com"})
    access_token = await verifier.verify_token(token_valido)
    assert access_token is not None
    assert access_token.client_id == "mcp_user@test.com"
    assert access_token.subject == "mcp_user@test.com"
    assert "gastos" in access_token.scopes

    token_invalido = "token.invalido.falso"
    resultado_invalido = await verifier.verify_token(token_invalido)
    assert resultado_invalido is None

    token_sin_sub = crear_access_token({"otra_cosa": 123})
    resultado_sin_sub = await verifier.verify_token(token_sin_sub)
    assert resultado_sin_sub is None


def test_mcp_server_initialization():
    from app.mcp.server import mcp

    assert mcp.name == "gastos-mcp"
    assert mcp.settings.streamable_http_path == "/"
    assert isinstance(mcp._token_verifier, JWTTokenVerifier)
    assert mcp.settings.auth is not None
    assert "gastos" in mcp.settings.auth.required_scopes
    assert mcp.settings.auth.validate_token_resource is False


@pytest.mark.anyio
async def test_mcp_registrar_gasto_tool():
    from app.mcp.server import mcp
    from app.database import Base, engine

    Base.metadata.create_all(bind=engine)
    resultado = await mcp.call_tool(
        "registrar_gasto",
        {"descripcion": "Cafe de prueba", "monto": 4.5, "categoria": "comida"},
    )
    # FastMCP call_tool returns a list of TextContent or dict
    if isinstance(resultado, tuple):
        resultado = resultado[0]
    texto = resultado[0].text if isinstance(resultado, list) else str(resultado)
    assert "Cafe de prueba" in texto
    assert "comida" in texto


@pytest.mark.anyio
async def test_mcp_listar_gastos_tool():
    from app.mcp.server import mcp
    from app.database import Base, engine

    Base.metadata.create_all(bind=engine)
    resultado = await mcp.call_tool("listar_gastos", {})
    if isinstance(resultado, tuple):
        resultado = resultado[0]
    texto = resultado[0].text if isinstance(resultado, list) else str(resultado)
    assert "Cafe de prueba" in texto or "id" in texto


@pytest.mark.anyio
async def test_mcp_error_limite_excedido_tool():
    from app.mcp.server import mcp
    from app.database import Base, engine

    Base.metadata.create_all(bind=engine)
    resultado = await mcp.call_tool(
        "registrar_gasto",
        {"descripcion": "Gasto exorbitante", "monto": 600.0, "categoria": "comida"},
    )
    if isinstance(resultado, tuple):
        resultado = resultado[0]
    texto = resultado[0].text if isinstance(resultado, list) else str(resultado)
    assert "error" in texto
    assert "supera el límite" in texto


@pytest.mark.anyio
async def test_mcp_tool_con_usuario_autenticado_y_token_invalido():
    from mcp.server.auth.middleware.auth_context import auth_context_var, AuthenticatedUser
    from mcp.server.auth.provider import AccessToken
    from app.mcp.server import mcp
    from app.database import Base, engine, SessionLocal
    from app.repositories import usuarios as usuarios_repository

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not usuarios_repository.obtener_por_email(db, "autenticado@test.com"):
            usuarios_repository.guardar(db, "autenticado@test.com", "hash123")
    finally:
        db.close()

    token = AccessToken(
        token="jwt_real",
        client_id="autenticado@test.com",
        scopes=["gastos"],
        subject="autenticado@test.com",
    )
    token_context = auth_context_var.set(AuthenticatedUser(token))

    try:
        resultado = await mcp.call_tool(
            "registrar_gasto",
            {"descripcion": "Gasto usuario auth", "monto": 20.0, "categoria": "transporte"},
        )
        if isinstance(resultado, tuple):
            resultado = resultado[0]
        texto = resultado[0].text if isinstance(resultado, list) else str(resultado)
        assert "Gasto usuario auth" in texto

        # Ahora con token de un usuario que no existe en DB
        token_fantasma = AccessToken(
            token="jwt_fantasma",
            client_id="fantasma@test.com",
            scopes=["gastos"],
            subject="fantasma@test.com",
        )
        auth_context_var.set(AuthenticatedUser(token_fantasma))
        res_fantasma = await mcp.call_tool(
            "registrar_gasto",
            {"descripcion": "No deberia pasar", "monto": 10.0, "categoria": "ocio"},
        )
        if isinstance(res_fantasma, tuple):
            res_fantasma = res_fantasma[0]
        texto_fantasma = res_fantasma[0].text if isinstance(res_fantasma, list) else str(res_fantasma)
        assert "error" in texto_fantasma
        assert "no corresponde a ningún usuario" in texto_fantasma
    finally:
        auth_context_var.reset(token_context)


def test_mcp_streamable_http_endpoint_mounted():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.security import crear_access_token

    client = TestClient(app)
    resp_sin_auth = client.post("/mcp/")
    assert resp_sin_auth.status_code == 401
    assert "WWW-Authenticate" in resp_sin_auth.headers

    token = crear_access_token({"sub": "demo@curso.com"})
    with TestClient(app) as client_lifespan:
        resp_con_auth = client_lifespan.post(
            "/mcp/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp_con_auth.status_code != 401


def test_vscode_mcp_config_valida():
    import json
    import os

    mcp_json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".vscode", "mcp.json")
    assert os.path.exists(mcp_json_path)

    with open(mcp_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "servers" in data
    assert "gastos-mcp" in data["servers"]
    assert data["servers"]["gastos-mcp"]["type"] == "http"
    assert data["servers"]["gastos-mcp"]["url"] == "http://127.0.0.1:8000/mcp/"
    assert "Authorization" in data["servers"]["gastos-mcp"]["headers"]

    assert "gastos-mcp-stdio" in data["servers"]
    assert data["servers"]["gastos-mcp-stdio"]["type"] == "stdio"
    assert data["servers"]["gastos-mcp-stdio"]["command"] == "uv"

