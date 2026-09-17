import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.repositories import usuarios as usuarios_repository
from app.repositories import gastos as gastos_repository
from app.services import gastos as gastos_service

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")


@pytest.fixture
def db_session():
    connect_args = {"check_same_thread": False} if TEST_DATABASE_URL.startswith("sqlite") else {}
    engine = create_engine(TEST_DATABASE_URL, connect_args=connect_args)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_registrar_y_listar_gasto_integracion(db_session):
    usuario = usuarios_repository.guardar(db_session, "test@ejemplo.com", "hash-de-prueba")

    gastos_service.registrar_gasto(
        db_session, usuario.id, "Almuerzo", 12.50, "comida", repo=gastos_repository
    )

    gastos = gastos_service.listar_gastos(db_session, usuario.id, repo=gastos_repository)

    assert len(gastos) == 1
    assert gastos[0]["descripcion"] == "Almuerzo"


def test_limite_por_categoria_integracion(db_session):
    usuario = usuarios_repository.guardar(db_session, "otro@ejemplo.com", "hash-de-prueba")

    gastos_service.registrar_gasto(db_session, usuario.id, "Gasto 1", 490.0, "comida", repo=gastos_repository)

    with pytest.raises(gastos_service.LimiteExcedidoError):
        gastos_service.registrar_gasto(db_session, usuario.id, "Gasto 2", 50.0, "comida", repo=gastos_repository)


def test_aislamiento_entre_usuarios_integracion(db_session):
    usuario_a = usuarios_repository.guardar(db_session, "usuario_a@ejemplo.com", "hash-a")
    usuario_b = usuarios_repository.guardar(db_session, "usuario_b@ejemplo.com", "hash-b")

    # Registrar gastos para Usuario A
    gastos_service.registrar_gasto(db_session, usuario_a.id, "Gasto A1", 100.0, "comida", repo=gastos_repository)
    gastos_service.registrar_gasto(db_session, usuario_a.id, "Gasto A2", 50.0, "transporte", repo=gastos_repository)

    # Registrar gastos para Usuario B
    gastos_service.registrar_gasto(db_session, usuario_b.id, "Gasto B1", 200.0, "comida", repo=gastos_repository)

    # Comprobar que Usuario A sólo ve sus 2 gastos
    gastos_a = gastos_service.listar_gastos(db_session, usuario_a.id, repo=gastos_repository)
    assert len(gastos_a) == 2
    assert all(g["descripcion"].startswith("Gasto A") for g in gastos_a)

    # Comprobar que Usuario B sólo ve su 1 gasto
    gastos_b = gastos_service.listar_gastos(db_session, usuario_b.id, repo=gastos_repository)
    assert len(gastos_b) == 1
    assert gastos_b[0]["descripcion"] == "Gasto B1"

    # Comprobar totales por categoría aislados
    total_comida_a = gastos_repository.total_por_categoria(db_session, usuario_a.id, "comida")
    assert total_comida_a == 100.0

    total_comida_b = gastos_repository.total_por_categoria(db_session, usuario_b.id, "comida")
    assert total_comida_b == 200.0
