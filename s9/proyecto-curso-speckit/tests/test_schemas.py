import pytest
from pydantic import ValidationError
from app.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.schemas.gasto import GastoCreate, GastoResponse


def test_usuario_schemas_password_no_expuesto():
    user_in = UsuarioCreate(email="test@domain.com", password="secret-password")
    assert user_in.email == "test@domain.com"
    assert user_in.password == "secret-password"

    user_out = UsuarioResponse(id=1, email="test@domain.com")
    data = user_out.model_dump()
    assert "password" not in data
    assert "hashed_password" not in data
    assert data["id"] == 1
    assert data["email"] == "test@domain.com"

    with pytest.raises(ValidationError):
        UsuarioCreate(email="not-an-email", password="123")


def test_gasto_schemas_validacion():
    gasto_in = GastoCreate(descripcion="Cena", monto=45.5, categoria="comida")
    assert gasto_in.descripcion == "Cena"
    assert gasto_in.monto == 45.5
    assert gasto_in.categoria == "comida"

    gasto_out = GastoResponse(id=10, descripcion="Cena", monto=45.5, categoria="comida")
    assert gasto_out.id == 10
    assert gasto_out.monto == 45.5

    # Invalid types
    with pytest.raises(ValidationError):
        GastoCreate(descripcion="Cena", monto="no-un-monto", categoria="comida")
