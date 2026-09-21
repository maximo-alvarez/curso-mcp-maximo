"""Servicio de lógica de negocio para gestión y autenticación de usuarios."""
from typing import Any
from app.repositories import usuarios as usuarios_repository
from app.security import hashear_password, verificar_password, crear_access_token


class EmailYaRegistradoError(Exception):
    """Excepción cuando el correo ya existe en el sistema."""
    pass


class CredencialesInvalidasError(Exception):
    """Excepción cuando el usuario no existe o la contraseña no coincide."""
    pass


def registrar_usuario(db: Any, email: str, password: str, repo=usuarios_repository) -> Any:
    """Registra un nuevo usuario verificando que el email no se encuentre duplicado."""
    usuario_existente = repo.obtener_por_email(db, email=email)
    if usuario_existente is not None:
        raise EmailYaRegistradoError("El email ya está registrado")

    password_hasheada = hashear_password(password)
    return repo.guardar(db, email=email, hashed_password=password_hasheada)


def autenticar_usuario(db: Any, email: str, password: str, repo=usuarios_repository) -> dict[str, str]:
    """Valida las credenciales de un usuario y emite un token de acceso JWT firmado."""
    usuario = repo.obtener_por_email(db, email=email)
    if usuario is None or not verificar_password(password, usuario.hashed_password):
        raise CredencialesInvalidasError("Credenciales inválidas")

    token = crear_access_token(data={"sub": usuario.email})
    return {"access_token": token, "token_type": "bearer"}
