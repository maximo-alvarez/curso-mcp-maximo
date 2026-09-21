"""Herramientas MCP para el Sistema de Reservas."""
from sqlalchemy.orm import Session
from mcp.server.auth.middleware.auth_context import get_access_token

from app.config import settings
from app.database import Base, SessionLocal, engine
import app.models.reserva  # noqa: F401
import app.models.usuario  # noqa: F401
from app.mcp.server import mcp_server

from app.repositories import usuarios as usuarios_repository
from app.services.reservas import (
    FechaPasadaError,
    HorarioInvalidoError,
    HorarioSolapadoError,
    NoAutorizadoError,
    ReservaNoEncontradaError,
    cancelar_reserva as cancelar_reserva_service,
    crear_reserva as crear_reserva_service,
    listar_reservas as listar_reservas_service,
)
from app.services.usuarios import registrar_usuario


def _obtener_db() -> Session:
    Base.metadata.create_all(bind=engine)
    return SessionLocal()


def _obtener_usuario_id(db: Session) -> int:
    """Resuelve la identidad del usuario a partir del token Bearer o usuario demo (Art. VI.4)."""
    token_info = get_access_token()
    if token_info and token_info.subject:
        subject = token_info.subject
        if subject.isdigit():
            return int(subject)
        usuario = usuarios_repository.obtener_por_email(db, subject)
        if usuario is not None:
            return usuario.id
        nuevo_usuario = registrar_usuario(db, email=subject, password="DefaultPassword123!")
        return nuevo_usuario.id

    demo_email = settings.MCP_DEMO_USER_EMAIL
    usuario_demo = usuarios_repository.obtener_por_email(db, demo_email)
    if usuario_demo is None:
        usuario_demo = registrar_usuario(db, email=demo_email, password=settings.MCP_DEMO_PASSWORD)
    return usuario_demo.id


@mcp_server.tool(
    name="crear_reserva",
    description=(
        "Registra una reserva para el espacio compartido indicando fecha (YYYY-MM-DD), "
        "hora de inicio (HH:MM) y hora de fin (HH:MM). Valida que la fecha sea igual o "
        "posterior a hoy y que no existan solapamientos con otras reservas activas."
    ),
)
def crear_reserva(fecha: str, hora_inicio: str, hora_fin: str) -> dict:
    """Crea una reserva delegando a services.reservas (Art. VI.1) y retornando diccionarios estructurados (Art. VI.3)."""
    db = _obtener_db()
    try:
        usuario_id = _obtener_usuario_id(db)
        return crear_reserva_service(
            db,
            usuario_id=usuario_id,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
        )
    except (HorarioSolapadoError, HorarioInvalidoError, FechaPasadaError) as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


@mcp_server.tool(
    name="listar_reservas",
    description="Lista las reservas del usuario autenticado en la sesión MCP, con soporte de paginación (skip y limit).",
)
def listar_reservas(skip: int = 0, limit: int = 20) -> list[dict] | dict:
    """Lista reservas propias delegando a services.reservas (Art. VI.1)."""
    db = _obtener_db()
    try:
        usuario_id = _obtener_usuario_id(db)
        return listar_reservas_service(
            db,
            usuario_id=usuario_id,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


@mcp_server.tool(
    name="cancelar_reserva",
    description=(
        "Cancela una reserva activa del usuario autenticado liberando el horario. "
        "Requiere confirmacion=True para proceder con la cancelación destructiva."
    ),
)
def cancelar_reserva(reserva_id: int, confirmacion: bool = False) -> dict:
    """Cancela una reserva con confirmación obligatoria en 2 pasos gestionada por el servidor (Art. VI.5)."""
    if not confirmacion:
        return {
            "status": "confirmation_required",
            "message": (
                f"La cancelación liberará el horario de la reserva #{reserva_id} "
                f"para otros usuarios. Confirme la operación ejecutando "
                f"cancelar_reserva(reserva_id={reserva_id}, confirmacion=True)."
            ),
        }

    db = _obtener_db()
    try:
        usuario_id = _obtener_usuario_id(db)
        cancelar_reserva_service(db, usuario_id=usuario_id, reserva_id=reserva_id)
        return {
            "status": "success",
            "message": f"Reserva #{reserva_id} cancelada exitosamente",
        }
    except (NoAutorizadoError, ReservaNoEncontradaError) as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


crear_reserva_tool = crear_reserva
listar_reservas_tool = listar_reservas
cancelar_reserva_tool = cancelar_reserva
