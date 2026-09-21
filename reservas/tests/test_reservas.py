import pytest
from app.services.reservas import (
    FechaPasadaError,
    HorarioInvalidoError,
    HorarioSolapadoError,
    NoAutorizadoError,
    ReservaNoEncontradaError,
    cancelar_reserva,
    crear_reserva,
    listar_reservas,
)


class RepositorioReservasFalso:
    """Implementación de repositorio en memoria para pruebas unitarias sin dependencias de base de datos."""

    def __init__(self):
        self.reservas: list[dict] = []
        self.next_id = 1

    def guardar(self, db, usuario_id: int, fecha: str, hora_inicio: str, hora_fin: str) -> dict:
        reserva = {
            "id": self.next_id,
            "usuario_id": usuario_id,
            "fecha": fecha,
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin,
            "estado": "ACTIVA",
        }
        self.reservas.append(reserva)
        self.next_id += 1
        return reserva

    def buscar_solapamiento(self, db, fecha: str, hora_inicio: str, hora_fin: str) -> bool:
        for r in self.reservas:
            if r["fecha"] == fecha and r["estado"] == "ACTIVA":
                # Condición matemática de solapamiento
                if r["hora_inicio"] < hora_fin and r["hora_fin"] > hora_inicio:
                    return True
        return False

    def listar_por_usuario(self, db, usuario_id: int, skip: int = 0, limit: int = 20) -> list[dict]:
        filtradas = [r for r in self.reservas if r["usuario_id"] == usuario_id]
        return filtradas[skip : skip + limit]

    def buscar_por_id(self, db, reserva_id: int) -> dict | None:
        for r in self.reservas:
            if r["id"] == reserva_id:
                return r
        return None

    def cancelar(self, db, reserva_id: int) -> bool:
        for r in self.reservas:
            if r["id"] == reserva_id:
                r["estado"] = "CANCELADA"
                return True
        return False


def test_crear_reserva_exitosa():
    repo = RepositorioReservasFalso()
    reserva = crear_reserva(
        db=None,
        usuario_id=1,
        fecha="2099-10-15",
        hora_inicio="10:00",
        hora_fin="12:00",
        repo=repo,
    )

    assert reserva["id"] == 1
    assert reserva["usuario_id"] == 1
    assert reserva["fecha"] == "2099-10-15"
    assert reserva["hora_inicio"] == "10:00"
    assert reserva["hora_fin"] == "12:00"
    assert reserva["estado"] == "ACTIVA"
    assert len(repo.reservas) == 1


def test_crear_reserva_horario_solapado_lanza_error():
    """Caso de Error 1: Intento de reserva que interseca una reserva existente en estado ACTIVA."""
    repo = RepositorioReservasFalso()
    # Reserva existente
    crear_reserva(
        db=None,
        usuario_id=1,
        fecha="2099-10-15",
        hora_inicio="10:00",
        hora_fin="12:00",
        repo=repo,
    )

    # Intento solapado (11:00 a 13:00)
    with pytest.raises(HorarioSolapadoError) as exc_info:
        crear_reserva(
            db=None,
            usuario_id=2,
            fecha="2099-10-15",
            hora_inicio="11:00",
            hora_fin="13:00",
            repo=repo,
        )

    assert "El horario solicitado se solapa con una reserva existente" in str(exc_info.value)
    assert len(repo.reservas) == 1


def test_crear_reserva_hora_fin_menor_o_igual_lanza_error():
    """Caso de Error 2: Hora fin menor o igual que hora de inicio."""
    repo = RepositorioReservasFalso()

    # Hora fin menor que hora inicio
    with pytest.raises(HorarioInvalidoError) as exc_info1:
        crear_reserva(
            db=None,
            usuario_id=1,
            fecha="2099-10-15",
            hora_inicio="14:00",
            hora_fin="12:00",
            repo=repo,
        )
    assert "La hora de fin debe ser posterior a la hora de inicio" in str(exc_info1.value)

    # Hora fin igual que hora inicio
    with pytest.raises(HorarioInvalidoError) as exc_info2:
        crear_reserva(
            db=None,
            usuario_id=1,
            fecha="2099-10-15",
            hora_inicio="10:00",
            hora_fin="10:00",
            repo=repo,
        )
    assert "La hora de fin debe ser posterior a la hora de inicio" in str(exc_info2.value)


def test_crear_reserva_fecha_pasada_lanza_error():
    """Caso de Error 6: Fecha anterior a la fecha actual."""
    repo = RepositorioReservasFalso()

    with pytest.raises(FechaPasadaError) as exc_info:
        crear_reserva(
            db=None,
            usuario_id=1,
            fecha="2020-01-01",
            hora_inicio="10:00",
            hora_fin="12:00",
            repo=repo,
        )
    assert "No se pueden crear reservas en fechas pasadas" in str(exc_info.value)


def test_crear_reservas_contiguas_permitidas():
    """Verifica que reservas contiguas (ej. 10:00-11:00 y 11:00-12:00) no son rechazadas."""
    repo = RepositorioReservasFalso()

    r1 = crear_reserva(
        db=None,
        usuario_id=1,
        fecha="2099-10-15",
        hora_inicio="10:00",
        hora_fin="11:00",
        repo=repo,
    )
    r2 = crear_reserva(
        db=None,
        usuario_id=2,
        fecha="2099-10-15",
        hora_inicio="11:00",
        hora_fin="12:00",
        repo=repo,
    )

    assert r1["id"] == 1
    assert r2["id"] == 2
    assert len(repo.reservas) == 2


def test_listar_reservas_con_repositorio_falso():
    """Valida el listado paginado y aislamiento entre usuarios a través de la capa de servicios."""
    repo = RepositorioReservasFalso()

    # Crear 3 reservas para usuario 1
    crear_reserva(None, usuario_id=1, fecha="2099-10-01", hora_inicio="09:00", hora_fin="10:00", repo=repo)
    crear_reserva(None, usuario_id=1, fecha="2099-10-01", hora_inicio="10:00", hora_fin="11:00", repo=repo)
    crear_reserva(None, usuario_id=1, fecha="2099-10-01", hora_inicio="11:00", hora_fin="12:00", repo=repo)

    # Crear 1 reserva para usuario 2
    crear_reserva(None, usuario_id=2, fecha="2099-10-01", hora_inicio="14:00", hora_fin="15:00", repo=repo)

    # 1. Listar para usuario 1
    res_u1 = listar_reservas(db=None, usuario_id=1, skip=0, limit=10, repo=repo)
    assert len(res_u1) == 3
    assert all(r["usuario_id"] == 1 for r in res_u1)

    # 2. Paginación (skip=1, limit=1)
    res_pag = listar_reservas(db=None, usuario_id=1, skip=1, limit=1, repo=repo)
    assert len(res_pag) == 1
    assert res_pag[0]["hora_inicio"] == "10:00"

    # 3. Listar para usuario 2
    res_u2 = listar_reservas(db=None, usuario_id=2, skip=0, limit=10, repo=repo)
    assert len(res_u2) == 1
    assert res_u2[0]["usuario_id"] == 2

    # 4. Listar para usuario sin reservas
    res_u_vacio = listar_reservas(db=None, usuario_id=999, skip=0, limit=10, repo=repo)
    assert res_u_vacio == []


def test_cancelar_reserva_exitosa():
    repo = RepositorioReservasFalso()
    reserva = crear_reserva(None, usuario_id=1, fecha="2099-10-15", hora_inicio="10:00", hora_fin="12:00", repo=repo)

    resultado = cancelar_reserva(None, usuario_id=1, reserva_id=reserva["id"], repo=repo)
    assert resultado is True

    # Verificar que el estado cambió a CANCELADA
    reserva_actualizada = repo.buscar_por_id(None, reserva_id=reserva["id"])
    assert reserva_actualizada["estado"] == "CANCELADA"


def test_cancelar_reserva_ajena_lanza_no_autorizado():
    """Caso de Error 4: Intento de cancelación de una reserva perteneciente a otro usuario."""
    repo = RepositorioReservasFalso()
    reserva_usuario1 = crear_reserva(None, usuario_id=1, fecha="2099-10-15", hora_inicio="10:00", hora_fin="12:00", repo=repo)

    # Usuario 2 intenta cancelar la reserva de usuario 1
    with pytest.raises(NoAutorizadoError) as exc_info:
        cancelar_reserva(None, usuario_id=2, reserva_id=reserva_usuario1["id"], repo=repo)

    assert "No tiene permisos para cancelar esta reserva" in str(exc_info.value)

    # Verificar que la reserva sigue ACTIVA
    assert repo.buscar_por_id(None, reserva_id=reserva_usuario1["id"])["estado"] == "ACTIVA"


def test_cancelar_reserva_inexistente_lanza_error():
    """Caso de Error 5: Intento de cancelación de una reserva que no existe en el sistema."""
    repo = RepositorioReservasFalso()

    with pytest.raises(ReservaNoEncontradaError) as exc_info:
        cancelar_reserva(None, usuario_id=1, reserva_id=99999, repo=repo)

    assert "La reserva no existe" in str(exc_info.value)

