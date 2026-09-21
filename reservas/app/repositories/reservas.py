"""Operaciones de persistencia para reservas (módulo de funciones sueltas)."""
from sqlalchemy.orm import Session
from app.models.reserva import Reserva


def _reserva_to_dict(reserva: Reserva) -> dict:
    """Serializa la entidad Reserva a un diccionario de dominio desacoplado del ORM."""
    return {
        "id": reserva.id,
        "usuario_id": reserva.usuario_id,
        "fecha": reserva.fecha,
        "hora_inicio": reserva.hora_inicio,
        "hora_fin": reserva.hora_fin,
        "estado": reserva.estado,
    }


def guardar(db: Session, usuario_id: int, fecha: str, hora_inicio: str, hora_fin: str) -> dict:
    """Guarda una nueva reserva en estado ACTIVA y la devuelve como diccionario."""
    reserva = Reserva(
        usuario_id=usuario_id,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        estado="ACTIVA",
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return _reserva_to_dict(reserva)


def buscar_solapamiento(db: Session, fecha: str, hora_inicio: str, hora_fin: str) -> bool:
    """Verifica si existe solapamiento con alguna reserva en estado ACTIVA.

    Filtra estrictamente por fecha y estado == 'ACTIVA', evaluando la intersección:
    (hora_inicio < nueva_fin) and (hora_fin > nueva_inicio).
    """
    coincidencia = (
        db.query(Reserva)
        .filter(
            Reserva.fecha == fecha,
            Reserva.estado == "ACTIVA",
            Reserva.hora_inicio < hora_fin,
            Reserva.hora_fin > hora_inicio,
        )
        .first()
    )
    return coincidencia is not None


def listar_por_usuario(db: Session, usuario_id: int, skip: int = 0, limit: int = 20) -> list[dict]:
    """Lista las reservas correspondientes a un usuario con paginación (skip y limit).

    Filtra estrictamente por usuario_id garantizando aislamiento entre usuarios (Art. III.3)
    y retorna diccionarios planos sin fugar sesiones ORM (Art. VIII.1).
    """
    reservas = (
        db.query(Reserva)
        .filter(Reserva.usuario_id == usuario_id)
        .order_by(Reserva.fecha.asc(), Reserva.hora_inicio.asc(), Reserva.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_reserva_to_dict(r) for r in reservas]


def buscar_por_id(db: Session, reserva_id: int) -> dict | None:
    """Busca una reserva por su id y la retorna como diccionario si existe (Art. VIII.1)."""
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if reserva is None:
        return None
    return _reserva_to_dict(reserva)


def cancelar(db: Session, reserva_id: int) -> bool:
    """Actualiza lógicamente el estado de la reserva a CANCELADA (soft delete).

    Retorna True si la reserva fue encontrada y actualizada, False en caso contrario.
    """
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if reserva is None:
        return False
    reserva.estado = "CANCELADA"
    db.commit()
    db.refresh(reserva)
    return True
