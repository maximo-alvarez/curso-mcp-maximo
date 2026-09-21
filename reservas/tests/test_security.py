import pytest
import jwt
from app.security import (
    hash_password,
    verify_password,
    hashear_password,
    verificar_password,
    crear_access_token,
    decodificar_token,
    decodificar_access_token,
)


def test_password_hash_and_verify():
    password = "super-secret-password-123"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong-password", hashed) is False

    # Check aliases
    hashed2 = hashear_password("otra-clave")
    assert verificar_password("otra-clave", hashed2) is True


def test_jwt_encode_and_decode():
    payload = {"sub": "user@test.com", "user_id": 42}
    token = crear_access_token(payload)

    assert isinstance(token, str)
    decoded = decodificar_token(token)
    assert decoded["sub"] == "user@test.com"
    assert decoded["user_id"] == 42
    assert "exp" in decoded

    decoded2 = decodificar_access_token(token)
    assert decoded2["sub"] == "user@test.com"


def test_jwt_invalid_token():
    with pytest.raises(jwt.InvalidTokenError):
        decodificar_token("invalid.jwt.token")
