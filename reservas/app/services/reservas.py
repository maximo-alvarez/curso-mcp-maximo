"""Lógica de negocio para gestión y control de reservas de espacio compartido.

Cumple estrictamente con la Constitución:
- Artículo I.2: Cero imports de SQLAlchemy, Session o detalles de persistencia.
- Artículo II.1: Principio de Responsabilidad Única (SRP) separando validaciones de orquestación.
- Artículo II.3: Inyección de dependencias (DIP) mediante parámetro por defecto repo=reservas_repository.
"""
from typing import Any
from app.repositories import reservas as reservas_repository
from app.utils.validadores import (
    validar_fecha_futura_o_presente,
    validar_orden_horas,
)


class HorarioSolapadoError(Exception):
    """Excepción cuando el horario coincide con una reserva en estado ACTIVA."""
    pass


class HorarioInvalidoError(Exception):
    """Excepción cuando hora_fin <= hora_inicio o el formato es incorrecto."""
    pass


class FechaPasadaError(Exception):
    """Excepción cuando la fecha solicitada es anterior a la fecha actual."""
    pass


class ReservaNoEncontradaError(Exception):
    """Excepción cuando la reserva solicitada no existe."""
    pass


class NoAutorizadoError(Exception):
    """Excepción cuando un usuario intenta operar sobre una reserva ajena."""
    pass


def _validar_fecha(fecha: str) -> None:
    """Valida que la fecha tenga formato válido y sea igual o posterior al día de hoy."""
    if not validar_fecha_futura_o_presente(fecha):
        raise FechaPasadaError("No se pueden crear reservas en fechas pasadas")


def _validar_horario(hora_inicio: str, hora_fin: str) -> None:
    """Valida que la hora de fin sea estrictamente posterior a la hora de inicio."""
    if not validar_orden_horas(hora_inicio, hora_fin):
        raise HorarioInvalidoError("La hora de fin debe ser posterior a la hora de inicio")


def crear_reserva(
    db: Any,
    usuario_id: int,
    fecha: str,
    hora_inicio: str,
    hora_fin: str,
    repo=reservas_repository,
) -> dict:
    """Orquesta la creación de una reserva previa validación de fecha, horario y solapamientos."""
    _validar_fecha(fecha)
    _validar_horario(hora_inicio, hora_fin)

    if repo.buscar_solapamiento(db, fecha=fecha, hora_inicio=hora_inicio, hora_fin=hora_fin):
        raise HorarioSolapadoError("El horario solicitado se solapa con una reserva existente")

    return repo.guardar(
        db,
        usuario_id=usuario_id,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
    )


def listar_reservas(
    db: Any,
    usuario_id: int,
    skip: int = 0,
    limit: int = 20,
    repo=reservas_repository,
) -> list[dict]:
    """Lista las reservas correspondientes a un usuario con paginación."""
    return repo.listar_por_usuario(db, usuario_id=usuario_id, skip=skip, limit=limit)


def cancelar_reserva(
    db: Any,
    usuario_id: int,
    reserva_id: int,
    repo=reservas_repository,
) -> bool:
    """Cancela una reserva propia verificando existencia y propiedad."""
    reserva = repo.buscar_por_id(db, reserva_id=reserva_id)
    if reserva is None:
        raise ReservaNoEncontradaError("La reserva no existe")

    if reserva["usuario_id"] != usuario_id:
        raise NoAutorizadoError("No tiene permisos para cancelar esta reserva")

    return repo.cancelar(db, reserva_id=reserva_id)
