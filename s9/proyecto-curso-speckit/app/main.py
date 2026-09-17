import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.logging_config import configurar_logging
from app.routers import usuarios, gastos
from app.mcp.server import mcp as mcp_server

configurar_logging(settings.log_level)
logger = logging.getLogger(__name__)


class DynamicMCPApp:
    def __init__(self, mcp):
        self.mcp = mcp
        self._app = mcp.streamable_http_app()

    def refresh(self):
        self.mcp._session_manager = None
        self._app = self.mcp.streamable_http_app()

    async def __call__(self, scope, receive, send):
        await self._app(scope, receive, send)


# Streamable-HTTP: sub-app ASGI montable en FastAPI delegando al session manager activo
mcp_app = DynamicMCPApp(mcp_server)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # mcp_app trae su propio lifespan (arranca el session manager de streamable-http).
    # FastAPI NO lo arranca solo por estar montado con app.mount() -- hay que entrar a él
    # explícitamente, o las conexiones a /mcp fallan o cuelgan.
    if hasattr(mcp_server, "session_manager") and mcp_server.session_manager is not None:
        if mcp_server.session_manager._has_started:
            mcp_app.refresh()
    async with mcp_server.session_manager.run():
        yield


app = FastAPI(title="API de Control de Gastos", lifespan=lifespan)
app.include_router(usuarios.router)
app.include_router(gastos.router)
app.mount("/mcp", mcp_app)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    inicio = time.perf_counter()
    response = await call_next(request)
    duracion_ms = (time.perf_counter() - inicio) * 1000
    logger.info(
        "%s %s -> %d (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duracion_ms,
    )
    return response


@app.exception_handler(Exception)
async def manejar_error_no_controlado(request: Request, exc: Exception):
    logger.exception("Error no controlado en %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})
