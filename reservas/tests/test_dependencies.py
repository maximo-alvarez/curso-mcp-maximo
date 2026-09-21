import pytest
from fastapi import HTTPException
from app.dependencies import get_reservas_repo, get_usuarios_repo, get_current_user
from app.security import crear_access_token


def test_get_reservas_repo():
    repo = get_reservas_repo()
    assert repo is not None
    assert hasattr(repo, "guardar")
    assert hasattr(repo, "listar_por_usuario")
    assert hasattr(repo, "buscar_solapamiento")
    assert hasattr(repo, "buscar_por_id")
    assert hasattr(repo, "cancelar")


def test_get_usuarios_repo():
    repo = get_usuarios_repo()
    assert repo is not None
    assert hasattr(repo, "obtener_por_email")
    assert hasattr(repo, "guardar")


def test_get_current_user_invalid_token():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token="invalid_token", db=None)
    assert exc_info.value.status_code == 401
    assert "credenciales" in exc_info.value.detail.lower()


def test_get_current_user_usuario_no_existe(monkeypatch):
    token = crear_access_token({"sub": "inexistente@example.com"})

    class DummyRepo:
        @staticmethod
        def obtener_por_email(db, email):
            return None

    monkeypatch.setattr("app.dependencies.usuarios_repository", DummyRepo)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=None)
    assert exc_info.value.status_code == 401
