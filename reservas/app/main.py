from contextlib import asynccontextmanager
import logging
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.logging_config import configurar_logging
from app.mcp.server import mcp_server
import app.mcp.tools.reservas  # noqa: F401
from app.routers.reservas import router as reservas_router
from app.routers.usuarios import router as usuarios_router

configurar_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    mcp_server.session_manager._has_started = False
    async with mcp_server.session_manager.run():
        yield



app = FastAPI(title="API del Sistema de Reservas", lifespan=lifespan)
app.include_router(usuarios_router)
app.include_router(reservas_router)
app.mount("/mcp", mcp_server.streamable_http_app())



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
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"},
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}
