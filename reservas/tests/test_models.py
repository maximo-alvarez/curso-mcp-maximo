import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.reserva import Reserva
from app.models.usuario import Usuario


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


def test_modelo_usuario_creacion_e_indice(db_session):
    usuario = Usuario(
        email="usuario@example.com",
        hashed_password="hash_bcrypt_seguro_simulado",
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)

    assert usuario.id is not None
    assert usuario.email == "usuario@example.com"
    assert usuario.hashed_password == "hash_bcrypt_seguro_simulado"

    # Verificar restricción de unicidad en email
    usuario_duplicado = Usuario(
        email="usuario@example.com",
        hashed_password="otro_hash_seguro",
    )
    db_session.add(usuario_duplicado)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_modelo_reserva_atributos_e_indices(db_session):
    # 1. Crear usuario propietario
    usuario = Usuario(
        email="reserva_owner@example.com",
        hashed_password="hash_bcrypt_seguro",
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)

    # 2. Crear reserva asociada
    reserva = Reserva(
        usuario_id=usuario.id,
        fecha="2026-10-01",
        hora_inicio="10:00",
        hora_fin="12:00",
    )
    db_session.add(reserva)
    db_session.commit()
    db_session.refresh(reserva)

    # 3. Validar atributos y valores por defecto
    assert reserva.id is not None
    assert reserva.usuario_id == usuario.id
    assert reserva.fecha == "2026-10-01"
    assert reserva.hora_inicio == "10:00"
    assert reserva.hora_fin == "12:00"
    assert reserva.estado == "ACTIVA"

    # 4. Validar navegación bidireccional
    assert reserva.usuario.email == "reserva_owner@example.com"
    assert len(usuario.reservas) == 1
    assert usuario.reservas[0].id == reserva.id

    # 5. Validar existencia y columnas del índice compuesto (fecha, estado)
    table_indexes = {idx.name: [c.name for c in idx.columns] for idx in Reserva.__table__.indexes}
    assert "ix_reservas_fecha_estado" in table_indexes
    assert table_indexes["ix_reservas_fecha_estado"] == ["fecha", "estado"]
    assert "ix_reservas_usuario_id" in table_indexes
