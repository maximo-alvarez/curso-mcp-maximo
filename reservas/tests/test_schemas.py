import pytest
from pydantic import ValidationError

from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.schemas.reserva import ReservaCreate, ReservaOut
from app.schemas.usuario import Token, UsuarioCreate, UsuarioOut


def test_usuario_schemas_password_no_expuesto():
    # 1. Validación de UsuarioCreate exitoso
    create_schema = UsuarioCreate(email="test@example.com", password="password123")
    assert create_schema.email == "test@example.com"
    assert create_schema.password == "password123"

    # 2. Validación de formato estricto de email en UsuarioCreate
    with pytest.raises(ValidationError):
        UsuarioCreate(email="no-es-un-email", password="password123")

    # 3. Conversión desde modelo de dominio/ORM hacia UsuarioOut
    usuario_db = Usuario(
        id=42,
        email="test@example.com",
        hashed_password="hash_secreto_que_nunca_debe_filtrarse",
    )
    usuario_out = UsuarioOut.model_validate(usuario_db)

    assert usuario_out.id == 42
    assert usuario_out.email == "test@example.com"

    # Verificación estricta: ningún campo de contraseña existe o se expone
    assert not hasattr(usuario_out, "password")
    assert not hasattr(usuario_out, "hashed_password")

    dumped = usuario_out.model_dump()
    assert "password" not in dumped
    assert "hashed_password" not in dumped
    assert set(dumped.keys()) == {"id", "email"}


def test_token_schema():
    token = Token(access_token="fake_jwt_token")
    assert token.access_token == "fake_jwt_token"
    assert token.token_type == "bearer"


def test_reserva_schemas_serializacion():
    # 1. Entrada con ReservaCreate
    reserva_in_data = {
        "fecha": "2026-10-15",
        "hora_inicio": "10:00",
        "hora_fin": "12:00",
    }
    reserva_in = ReservaCreate(**reserva_in_data)
    assert reserva_in.fecha == "2026-10-15"
    assert reserva_in.hora_inicio == "10:00"
    assert reserva_in.hora_fin == "12:00"
    assert reserva_in.model_dump() == reserva_in_data

    # Verificar que ReservaCreate no contiene id, usuario_id ni estado
    assert "id" not in ReservaCreate.model_fields
    assert "usuario_id" not in ReservaCreate.model_fields
    assert "estado" not in ReservaCreate.model_fields

    # 2. Salida con ReservaOut desde modelo ORM
    reserva_orm = Reserva(
        id=99,
        usuario_id=5,
        fecha="2026-10-15",
        hora_inicio="10:00",
        hora_fin="12:00",
        estado="ACTIVA",
    )
    reserva_out = ReservaOut.model_validate(reserva_orm)
    assert reserva_out.id == 99
    assert reserva_out.usuario_id == 5
    assert reserva_out.fecha == "2026-10-15"
    assert reserva_out.hora_inicio == "10:00"
    assert reserva_out.hora_fin == "12:00"
    assert reserva_out.estado == "ACTIVA"

    # 3. Salida con ReservaOut desde diccionario
    reserva_dict = {
        "id": 100,
        "usuario_id": 6,
        "fecha": "2026-10-16",
        "hora_inicio": "14:00",
        "hora_fin": "15:00",
        "estado": "CANCELADA",
    }
    reserva_out_dict = ReservaOut.model_validate(reserva_dict)
    assert reserva_out_dict.id == 100
    assert reserva_out_dict.estado == "CANCELADA"
