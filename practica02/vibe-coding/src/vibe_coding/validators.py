import re
from typing import Dict, List, Any

# Almacenamiento en memoria de usuarios
usuarios: List[Dict[str, Any]] = []

def validar_contrasena(password: str) -> Dict[str, Any]:
    """
    Valida si una contraseña cumple con los requisitos de seguridad:
    - No vacía
    - Mínimo 8 caracteres
    - Al menos una letra mayúscula
    - Al menos una letra minúscula
    - Al menos un número
    - Al menos un carácter especial (!@#$%^&*(),.?":{}|<>)
    """
    errores = []

    if not password:
        return {
            "valida": False,
            "errores": ["La contraseña no puede estar vacía."]
        }

    if len(password) < 8:
        errores.append("Debe tener al menos 8 caracteres.")

    if not re.search(r"[A-Z]", password):
        errores.append("Debe contener al menos una letra mayúscula.")

    if not re.search(r"[a-z]", password):
        errores.append("Debe contener al menos una letra minúscula.")

    if not re.search(r"\d", password):
        errores.append("Debe contener al menos un número.")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errores.append("Debe contener al menos un carácter especial (!@#$%^&*(),.?\":{}|<>).")

    return {
        "valida": len(errores) == 0,
        "errores": errores
    }

def validar_email(email: str) -> Dict[str, Any]:
    """
    Valida si una dirección de correo electrónico tiene un formato válido.
    """
    errores = []

    if not email:
        return {
            "valida": False,
            "errores": ["El correo electrónico no puede estar vacío."]
        }

    patron_email = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(patron_email, email):
        errores.append("El formato del correo electrónico no es válido.")

    return {
        "valida": len(errores) == 0,
        "errores": errores
    }

def registrar_usuario(email: str, password: str = "", es_admin: bool = False) -> Dict[str, Any]:
    """
    Valida y registra un nuevo usuario.
    Para administradores (es_admin=True), la validación de contraseña es opcional.
    """
    res_email = validar_email(email)
    errores = []

    if not res_email["valida"]:
        errores.extend(res_email["errores"])

    if not es_admin:
        res_pwd = validar_contrasena(password)
        if not res_pwd["valida"]:
            errores.extend(res_pwd["errores"])

    # Verificar unicidad de email
    if any(u["email"].lower() == email.lower() for u in usuarios):
        errores.append("El correo electrónico ya está registrado.")

    if errores:
        return {
            "exito": False,
            "errores": errores
        }

    usuario = {
        "email": email,
        "password": password,
        "es_admin": es_admin
    }
    usuarios.append(usuario)

    return {
        "exito": True,
        "usuario": usuario
    }

def listar_usuarios() -> List[Dict[str, Any]]:
    """
    Retorna todos los usuarios registrados.
    """
    return usuarios

def limpiar_usuarios() -> None:
    """
    Limpia la lista en memoria (útil para pruebas).
    """
    usuarios.clear()
