from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base, get_db


def test_db_session_lifecycle():
    assert engine is not None
    assert SessionLocal is not None
    assert Base is not None

    db_gen = get_db()
    db = next(db_gen)
    assert isinstance(db, Session)

    try:
        pass
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass


def test_alembic_config_valida():
    import os
    assert os.path.exists("alembic.ini")
    assert os.path.exists("alembic/env.py")


def test_migracion_alembic_aplica_exitosamente():
    from alembic.config import Config
    from alembic import command
    from sqlalchemy import inspect
    from app.database import engine

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    inspector = inspect(engine)
    tablas = inspector.get_table_names()
    assert "usuarios" in tablas
    assert "gastos" in tablas
    assert "alembic_version" in tablas

    indices_usuarios = [idx["name"] for idx in inspector.get_indexes("usuarios")]
    assert any("email" in idx for idx in indices_usuarios)

    indices_gastos = [idx["name"] for idx in inspector.get_indexes("gastos")]
    assert any("usuario_id" in idx for idx in indices_gastos)

