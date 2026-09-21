"""Configuración e inicialización de la instancia del servidor FastMCP."""
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP

from app.config import settings
from app.mcp.auth import JWTTokenVerifier

auth_settings = AuthSettings(
    issuer_url=settings.MCP_ISSUER_URL,
    resource_server_url=settings.MCP_RESOURCE_URL,
    validate_token_resource=False,
)

mcp_server = FastMCP(
    "reservas-mcp",
    streamable_http_path="/",
    token_verifier=JWTTokenVerifier(),
    auth=auth_settings,
)

if __name__ == "__main__":
    import app.mcp.tools.reservas  # noqa: F401
    mcp_server.run(transport="stdio")

