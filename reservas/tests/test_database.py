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


def test_database_connect_args_sqlite():
    from app.database import connect_args
    from app.config import settings
    if settings.database_url.startswith("sqlite"):
        assert connect_args == {"check_same_thread": False}
    else:
        assert connect_args == {}


def test_alembic_config_valida():
    from pathlib import Path
    from alembic.config import Config
    root = Path(__file__).parent.parent
    assert (root / "alembic.ini").exists(), "alembic.ini debe existir"
    assert (root / "alembic" / "env.py").exists(), "alembic/env.py debe existir"
    assert (root / "alembic" / "script.py.mako").exists(), "alembic/script.py.mako debe existir"
    cfg = Config(str(root / "alembic.ini"))
    assert cfg.get_main_option("script_location") == "alembic"


def test_migracion_alembic_aplica_exitosamente():
    """Verifica la aplicación de la migración inicial de Alembic sobre reservas.db (Art. III.1)."""
    from pathlib import Path
    from alembic.config import Config
    from alembic import command
    from sqlalchemy import create_engine, inspect

    root = Path(__file__).parent.parent
    ini_path = root / "alembic.ini"
    cfg = Config(str(ini_path))

    # Ejecutar upgrade head
    command.upgrade(cfg, "head")

    # Inspeccionar reservas.db
    db_path = root / "reservas.db"
    assert db_path.exists(), "reservas.db debe existir tras aplicar migración"

    test_engine = create_engine(f"sqlite:///{db_path}")
    inspector = inspect(test_engine)
    tablas = inspector.get_table_names()

    assert "usuarios" in tablas
    assert "reservas" in tablas

    # Columnas de usuarios
    cols_usuarios = {c["name"] for c in inspector.get_columns("usuarios")}
    assert {"id", "email", "hashed_password"}.issubset(cols_usuarios)

    # Columnas de reservas
    cols_reservas = {c["name"] for c in inspector.get_columns("reservas")}
    assert {"id", "usuario_id", "fecha", "hora_inicio", "hora_fin", "estado"}.issubset(cols_reservas)

    # Índices en reservas
    indices_reservas = {idx["name"] for idx in inspector.get_indexes("reservas")}
    assert "ix_reservas_fecha_estado" in indices_reservas


