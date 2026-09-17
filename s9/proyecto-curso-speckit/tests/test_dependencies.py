import pytest
from fastapi import HTTPException
from app.dependencies import get_gastos_repo, get_current_user
from app.security import crear_access_token


def test_get_gastos_repo():
    repo = get_gastos_repo()
    assert repo is not None
    assert hasattr(repo, "guardar")
    assert hasattr(repo, "listar")
    assert hasattr(repo, "total_por_categoria")


def test_get_current_user_invalid_token():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token="invalid_token", db=None)
    assert exc_info.value.status_code == 401
