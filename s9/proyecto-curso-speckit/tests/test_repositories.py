import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.repositories import usuarios as usuarios_repository
from app.repositories import gastos as gastos_repository


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_usuario_repo_guardar_y_obtener(db_session):
    usuario = usuarios_repository.guardar(db_session, "test@correo.com", "hash123")
    assert usuario.id is not None
    assert usuario.email == "test@correo.com"

    encontrado = usuarios_repository.obtener_por_email(db_session, "test@correo.com")
    assert encontrado is not None
    assert encontrado.id == usuario.id
    assert encontrado.email == "test@correo.com"

    no_existe = usuarios_repository.obtener_por_email(db_session, "inexistente@correo.com")
    assert no_existe is None


def test_gastos_repo_guardar(db_session):
    usuario = usuarios_repository.guardar(db_session, "gasto_user@test.com", "hash")
    resultado = gastos_repository.guardar(db_session, usuario.id, "Almuerzo", 15.0, "comida")

    assert isinstance(resultado, dict)
    assert resultado["descripcion"] == "Almuerzo"
    assert resultado["monto"] == 15.0
    assert resultado["categoria"] == "comida"
    assert "id" in resultado


def test_gastos_repo_total_por_categoria(db_session):
    usuario = usuarios_repository.guardar(db_session, "total_user@test.com", "hash")
    gastos_repository.guardar(db_session, usuario.id, "Comida 1", 20.0, "comida")
    gastos_repository.guardar(db_session, usuario.id, "Comida 2", 30.5, "comida")
    gastos_repository.guardar(db_session, usuario.id, "Taxi", 10.0, "transporte")

    total_comida = gastos_repository.total_por_categoria(db_session, usuario.id, "comida")
    assert total_comida == 50.5

    total_transporte = gastos_repository.total_por_categoria(db_session, usuario.id, "transporte")
    assert total_transporte == 10.0

    total_otros = gastos_repository.total_por_categoria(db_session, usuario.id, "otros")
    assert total_otros == 0.0


def test_gastos_repo_listar_con_filtro_usuario(db_session):
    u1 = usuarios_repository.guardar(db_session, "u1@test.com", "hash1")
    u2 = usuarios_repository.guardar(db_session, "u2@test.com", "hash2")

    gastos_repository.guardar(db_session, u1.id, "Gasto U1-A", 10.0, "comida")
    gastos_repository.guardar(db_session, u1.id, "Gasto U1-B", 20.0, "comida")
    gastos_repository.guardar(db_session, u2.id, "Gasto U2-A", 30.0, "transporte")

    # U1 should only see 2 expenses
    lista_u1 = gastos_repository.listar(db_session, u1.id, skip=0, limit=10)
    assert len(lista_u1) == 2
    assert all(g["descripcion"].startswith("Gasto U1") for g in lista_u1)

    # U2 should only see 1 expense
    lista_u2 = gastos_repository.listar(db_session, u2.id, skip=0, limit=10)
    assert len(lista_u2) == 1
    assert lista_u2[0]["descripcion"] == "Gasto U2-A"

    # Pagination test
    pag_1 = gastos_repository.listar(db_session, u1.id, skip=0, limit=1)
    assert len(pag_1) == 1
    assert pag_1[0]["descripcion"] == "Gasto U1-A"

    pag_2 = gastos_repository.listar(db_session, u1.id, skip=1, limit=1)
    assert len(pag_2) == 1
    assert pag_2[0]["descripcion"] == "Gasto U1-B"
