import pytest
from app.services.usuarios import (
    registrar_usuario,
    autenticar_usuario,
    EmailYaRegistradoError,
    CredencialesInvalidasError,
)


class UsuarioFalso:
    def __init__(self, id: int, email: str, hashed_password: str):
        self.id = id
        self.email = email
        self.hashed_password = hashed_password


class RepositorioUsuariosFalso:
    def __init__(self):
        self._usuarios: dict[str, UsuarioFalso] = {}

    def obtener_por_email(self, db, email: str):
        return self._usuarios.get(email)

    def guardar(self, db, email: str, hashed_password: str):
        user = UsuarioFalso(id=len(self._usuarios) + 1, email=email, hashed_password=hashed_password)
        self._usuarios[email] = user
        return user


def test_registrar_usuario_service():
    repo = RepositorioUsuariosFalso()
    usuario = registrar_usuario(None, "nuevo@test.com", "password123", repo=repo)

    assert usuario.email == "nuevo@test.com"
    assert usuario.id == 1

    with pytest.raises(EmailYaRegistradoError):
        registrar_usuario(None, "nuevo@test.com", "otra_clave", repo=repo)


def test_autenticar_usuario_service():
    repo = RepositorioUsuariosFalso()
    registrar_usuario(None, "user@test.com", "clave123", repo=repo)

    auth_user = autenticar_usuario(None, "user@test.com", "clave123", repo=repo)
    assert auth_user.email == "user@test.com"

    with pytest.raises(CredencialesInvalidasError):
        autenticar_usuario(None, "user@test.com", "clave_incorrecta", repo=repo)

    with pytest.raises(CredencialesInvalidasError):
        autenticar_usuario(None, "no_existe@test.com", "clave123", repo=repo)
