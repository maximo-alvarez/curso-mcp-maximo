import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.repositories import reservas as reservas_repo
from app.repositories import usuarios as usuarios_repo


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_usuario_repo_guardar_y_obtener(db_session):
    email = "test_repo@example.com"
    hashed_pwd = "hashed_secret_password_123"

    # 1. Guardar usuario
    usuario = usuarios_repo.guardar(db_session, email=email, hashed_password=hashed_pwd)
    assert usuario.id is not None
    assert usuario.email == email
    assert usuario.hashed_password == hashed_pwd

    # 2. Obtener por email existente
    encontrado = usuarios_repo.obtener_por_email(db_session, email=email)
    assert encontrado is not None
    assert encontrado.id == usuario.id
    assert encontrado.email == email

    # 3. Obtener por email inexistente
    no_encontrado = usuarios_repo.obtener_por_email(db_session, email="no_existe@example.com")
    assert no_encontrado is None


def test_reservas_repo_guardar(db_session):
    usuario = usuarios_repo.guardar(db_session, email="propietario@example.com", hashed_password="pwd")

    # Guardar reserva
    reserva_dict = reservas_repo.guardar(
        db_session,
        usuario_id=usuario.id,
        fecha="2026-10-15",
        hora_inicio="10:00",
        hora_fin="12:00",
    )

    # Validar que retorna un dict sin fugar objetos ORM
    assert isinstance(reserva_dict, dict)
    assert reserva_dict["id"] is not None
    assert reserva_dict["usuario_id"] == usuario.id
    assert reserva_dict["fecha"] == "2026-10-15"
    assert reserva_dict["hora_inicio"] == "10:00"
    assert reserva_dict["hora_fin"] == "12:00"
    assert reserva_dict["estado"] == "ACTIVA"


def test_reservas_repo_buscar_solapamiento(db_session):
    usuario = usuarios_repo.guardar(db_session, email="propietario_solapamiento@example.com", hashed_password="pwd")

    # 1. Crear reserva activa base: 2026-10-15 de 10:00 a 12:00
    reservas_repo.guardar(
        db_session,
        usuario_id=usuario.id,
        fecha="2026-10-15",
        hora_inicio="10:00",
        hora_fin="12:00",
    )

    # 2. Casos de solapamiento detectados (deben retornar True)
    # A. Solapamiento parcial al final (11:00 a 13:00)
    assert reservas_repo.buscar_solapamiento(db_session, "2026-10-15", "11:00", "13:00") is True
    # B. Solapamiento parcial al inicio (09:00 a 11:00)
    assert reservas_repo.buscar_solapamiento(db_session, "2026-10-15", "09:00", "11:00") is True
    # C. Contención total interna (10:30 a 11:30)
    assert reservas_repo.buscar_solapamiento(db_session, "2026-10-15", "10:30", "11:30") is True
    # D. Contención total envolvente (09:00 a 13:00)
    assert reservas_repo.buscar_solapamiento(db_session, "2026-10-15", "09:00", "13:00") is True
    # E. Coincidencia exacta (10:00 a 12:00)
    assert reservas_repo.buscar_solapamiento(db_session, "2026-10-15", "10:00", "12:00") is True

    # 3. Casos permitidos (deben retornar False)
    # F. Contiguo anterior (08:00 a 10:00) -> permitido
    assert reservas_repo.buscar_solapamiento(db_session, "2026-10-15", "08:00", "10:00") is False
    # G. Contiguo posterior (12:00 a 14:00) -> permitido
    assert reservas_repo.buscar_solapamiento(db_session, "2026-10-15", "12:00", "14:00") is False
    # H. Mismo horario pero en otra fecha (2026-10-16 de 10:00 a 12:00) -> permitido
    assert reservas_repo.buscar_solapamiento(db_session, "2026-10-16", "10:00", "12:00") is False

    # 4. Solapamiento contra reserva CANCELADA no debe bloquear
    reserva_cancelada = Reserva(
        usuario_id=usuario.id,
        fecha="2026-10-15",
        hora_inicio="16:00",
        hora_fin="18:00",
        estado="CANCELADA",
    )
    db_session.add(reserva_cancelada)
    db_session.commit()

    # Intentar reservar exactamente en el horario de la reserva cancelada -> permitido (False)
    assert reservas_repo.buscar_solapamiento(db_session, "2026-10-15", "16:00", "18:00") is False


def test_reservas_repo_listar_por_usuario(db_session):
    # 1. Crear dos usuarios
    user_a = usuarios_repo.guardar(db_session, email="user_a@example.com", hashed_password="pwd")
    user_b = usuarios_repo.guardar(db_session, email="user_b@example.com", hashed_password="pwd")

    # 2. Crear 4 reservas para user_a en diferentes horarios
    reservas_repo.guardar(db_session, usuario_id=user_a.id, fecha="2026-10-01", hora_inicio="08:00", hora_fin="09:00")
    reservas_repo.guardar(db_session, usuario_id=user_a.id, fecha="2026-10-01", hora_inicio="09:00", hora_fin="10:00")
    reservas_repo.guardar(db_session, usuario_id=user_a.id, fecha="2026-10-02", hora_inicio="10:00", hora_fin="11:00")
    reservas_repo.guardar(db_session, usuario_id=user_a.id, fecha="2026-10-02", hora_inicio="11:00", hora_fin="12:00")

    # 3. Crear 2 reservas para user_b
    reservas_repo.guardar(db_session, usuario_id=user_b.id, fecha="2026-10-01", hora_inicio="14:00", hora_fin="15:00")
    reservas_repo.guardar(db_session, usuario_id=user_b.id, fecha="2026-10-02", hora_inicio="16:00", hora_fin="17:00")

    # 4. Listar para user_a (sin paginación limit=10)
    lista_a = reservas_repo.listar_por_usuario(db_session, usuario_id=user_a.id, skip=0, limit=10)
    assert len(lista_a) == 4
    assert all(r["usuario_id"] == user_a.id for r in lista_a)
    assert all(isinstance(r, dict) for r in lista_a)

    # 5. Listar para user_a con paginación (skip=1, limit=2)
    lista_a_pag = reservas_repo.listar_por_usuario(db_session, usuario_id=user_a.id, skip=1, limit=2)
    assert len(lista_a_pag) == 2
    assert lista_a_pag[0]["hora_inicio"] == "09:00"
    assert lista_a_pag[1]["hora_inicio"] == "10:00"

    # 6. Listar para user_b: estricto aislamiento multiusuario (cero reservas de user_a)
    lista_b = reservas_repo.listar_por_usuario(db_session, usuario_id=user_b.id, skip=0, limit=10)
    assert len(lista_b) == 2
    assert all(r["usuario_id"] == user_b.id for r in lista_b)

    # 7. Listar para usuario sin reservas
    lista_vacia = reservas_repo.listar_por_usuario(db_session, usuario_id=9999, skip=0, limit=10)
    assert lista_vacia == []


def test_reservas_repo_buscar_y_cancelar(db_session):
    usuario = usuarios_repo.guardar(db_session, email="propietario_cancel@example.com", hashed_password="pwd")
    reserva = reservas_repo.guardar(
        db_session,
        usuario_id=usuario.id,
        fecha="2026-10-30",
        hora_inicio="10:00",
        hora_fin="12:00",
    )

    # 1. Buscar por id existente
    encontrada = reservas_repo.buscar_por_id(db_session, reserva["id"])
    assert encontrada is not None
    assert encontrada["id"] == reserva["id"]
    assert encontrada["usuario_id"] == usuario.id
    assert encontrada["estado"] == "ACTIVA"

    # 2. Buscar por id inexistente
    assert reservas_repo.buscar_por_id(db_session, 99999) is None

    # 3. Cancelar reserva existente (soft delete)
    cancelado = reservas_repo.cancelar(db_session, reserva["id"])
    assert cancelado is True

    # 4. Verificar que el estado ahora es CANCELADA
    actualizada = reservas_repo.buscar_por_id(db_session, reserva["id"])
    assert actualizada is not None
    assert actualizada["estado"] == "CANCELADA"

    # 5. Intentar cancelar id inexistente
    assert reservas_repo.cancelar(db_session, 99999) is False


