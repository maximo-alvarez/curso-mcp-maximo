"""Autenticación para el servidor MCP mediante JWT Bearer."""
import jwt
from mcp.server.auth.provider import AccessToken

from app.security import decodificar_token


class JWTTokenVerifier:
    """Verificador de tokens Bearer JWT para el protocolo MCP (Art. VI.4).

    Implementa el protocolo TokenVerifier de FastMCP, decodificando el token
    mediante app.security y validando la presencia del claim 'sub'.
    """

    async def verify_token(self, token: str) -> AccessToken | None:
        """Verifica el token JWT y devuelve un AccessToken si es válido, o None en caso de fallo."""
        try:
            payload = decodificar_token(token)
            sub = payload.get("sub")
            if not sub:
                return None

            return AccessToken(
                token=token,
                client_id=str(sub),
                scopes=[],
                expires_at=payload.get("exp"),
                subject=str(sub),
                claims=payload,
            )
        except (jwt.PyJWTError, Exception):
            return None
