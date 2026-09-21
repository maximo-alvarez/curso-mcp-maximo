import pytest
from app.security import decodificar_token, verificar_password
from app.services.usuarios import (
    CredencialesInvalidasError,
    EmailYaRegistradoError,
    autenticar_usuario,
    registrar_usuario,
)


class DummyUsuario:
    def __init__(self, id: int, email: str, hashed_password: str):
        self.id = id
        self.email = email
        self.hashed_password = hashed_password


class RepositorioUsuariosFalso:
    """Implementación en memoria para pruebas unitarias sin dependencias externas ni mocks."""

    def __init__(self):
        self.usuarios: dict[int, DummyUsuario] = {}
        self.next_id = 1

    def obtener_por_email(self, db, email: str):
        for u in self.usuarios.values():
            if u.email == email:
                return u
        return None

    def guardar(self, db, email: str, hashed_password: str):
        user = DummyUsuario(id=self.next_id, email=email, hashed_password=hashed_password)
        self.usuarios[self.next_id] = user
        self.next_id += 1
        return user


def test_registrar_usuario_service():
    repo = RepositorioUsuariosFalso()

    # 1. Registro exitoso
    usuario = registrar_usuario(None, email="usuario@example.com", password="Password123!", repo=repo)
    assert usuario.id == 1
    assert usuario.email == "usuario@example.com"
    assert verificar_password("Password123!", usuario.hashed_password)

    # 2. Intento de registro con email duplicado
    with pytest.raises(EmailYaRegistradoError) as exc_info:
        registrar_usuario(None, email="usuario@example.com", password="OtraPassword456!", repo=repo)
    assert "El email ya está registrado" in str(exc_info.value)


def test_autenticar_usuario_service():
    repo = RepositorioUsuariosFalso()
    registrar_usuario(None, email="usuario@example.com", password="PasswordCorrecta123!", repo=repo)

    # 1. Autenticación exitosa
    auth_data = autenticar_usuario(None, email="usuario@example.com", password="PasswordCorrecta123!", repo=repo)
    assert "access_token" in auth_data
    assert auth_data["token_type"] == "bearer"

    payload = decodificar_token(auth_data["access_token"])
    assert payload["sub"] == "usuario@example.com"

    # 2. Autenticación con contraseña errónea
    with pytest.raises(CredencialesInvalidasError) as exc_info:
        autenticar_usuario(None, email="usuario@example.com", password="PasswordIncorrecta!", repo=repo)
    assert "Credenciales inválidas" in str(exc_info.value)

    # 3. Autenticación con usuario inexistente
    with pytest.raises(CredencialesInvalidasError) as exc_info:
        autenticar_usuario(None, email="fantasma@example.com", password="CualquierPassword!", repo=repo)
    assert "Credenciales inválidas" in str(exc_info.value)
