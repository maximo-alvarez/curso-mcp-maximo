import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.repositories import usuarios as usuarios_repository
from app.repositories import gastos as gastos_repository

POSTGRES_URL = os.environ.get(
    "POSTGRES_TEST_URL",
    "postgresql+psycopg://gastos:gastos@localhost:5433/gastos",
)


def _is_postgres_available() -> bool:
    try:
        engine = create_engine(POSTGRES_URL, connect_args={"connect_timeout": 2})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _is_postgres_available(), reason="PostgreSQL no está disponible en localhost:5433")
def test_postgres_portabilidad():
    engine = create_engine(POSTGRES_URL)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Verificar portabilidad de persistencia guardando entidades en Postgres
        email = "postgres_user@test.com"
        # Limpiar si ya existía
        existente = usuarios_repository.obtener_por_email(session, email)
        if not existente:
            usuario = usuarios_repository.guardar(session, email, "hash_pg")
        else:
            usuario = existente

        assert usuario.id is not None
        assert usuario.email == email

        gasto = gastos_repository.guardar(
            session,
            usuario.id,
            "Gasto en Postgres",
            45.0,
            "transporte",
        )
        assert gasto["id"] is not None
        assert gasto["descripcion"] == "Gasto en Postgres"
        assert gasto["monto"] == 45.0

        total = gastos_repository.total_por_categoria(session, usuario.id, "transporte")
        assert total >= 45.0
    finally:
        session.close()
        engine.dispose()
