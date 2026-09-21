import os
from pathlib import Path
import socket
import pytest


def is_postgres_available(host: str = "localhost", port: int = 5433, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def test_docker_compose_config():
    """Verifica que docker-compose.yml exista y defina el servicio PostgreSQL en puerto 5433."""
    root = Path(__file__).parent.parent
    compose_file = root / "docker-compose.yml"
    assert compose_file.exists(), "docker-compose.yml debe existir en la raíz del proyecto"

    content = compose_file.read_text(encoding="utf-8")
    assert "postgres" in content.lower()
    assert "5433" in content
    assert "reservas_db" in content


@pytest.mark.skipif(
    not is_postgres_available(),
    reason="Servicio PostgreSQL no está disponible en localhost:5433 (se requiere docker compose up)",
)
def test_postgres_portabilidad():
    """Verifica portabilidad hacia PostgreSQL: creación de tablas y operaciones CRUD reales (Art. III.2)."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database import Base
    from app.models.reserva import Reserva
    from app.models.usuario import Usuario

    pg_url = os.getenv(
        "TEST_POSTGRES_URL",
        "postgresql+psycopg://postgres:password123@localhost:5433/reservas_db",
    )
    engine = create_engine(pg_url)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    db = TestingSession()
    try:
        # 1. Crear usuario en Postgres
        u = Usuario(email="pg_test@example.com", hashed_password="hashed_pwd")
        db.add(u)
        db.commit()
        db.refresh(u)
        assert u.id is not None

        # 2. Crear reserva en Postgres
        r = Reserva(
            usuario_id=u.id,
            fecha="2099-12-31",
            hora_inicio="10:00",
            hora_fin="12:00",
            estado="ACTIVA",
        )
        db.add(r)
        db.commit()
        db.refresh(r)
        assert r.id is not None
        assert r.estado == "ACTIVA"

        # Cleanup
        db.delete(r)
        db.delete(u)
        db.commit()
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
