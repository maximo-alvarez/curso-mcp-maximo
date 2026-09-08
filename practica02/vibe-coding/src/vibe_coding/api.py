from fastapi import FastAPI, HTTPException, status
from typing import List
import uvicorn

from vibe_coding.schemas import (
    PasswordValidationRequest,
    EmailValidationRequest,
    ValidationResponse,
    UserCreate,
    UserResponse,
    UserRegistrationResponse,
    ErrorResponse,
)
from vibe_coding.validators import (
    validar_contrasena,
    validar_email,
    registrar_usuario,
    listar_usuarios,
)

app = FastAPI(
    title="Vibe Coding API",
    description="API REST para validación de contraseñas, emails y gestión de usuarios con FastAPI",
    version="0.1.0",
)

@app.get("/health", tags=["Health"])
def health_check():
    """
    Verifica el estado del servicio.
    """
    return {"status": "ok", "service": "vibe-coding-api", "version": "0.1.0"}

@app.post(
    "/api/v1/validate/password",
    response_model=ValidationResponse,
    tags=["Validaciones"],
    summary="Valida reglas de complejidad de contraseña",
)
def validate_password_endpoint(payload: PasswordValidationRequest):
    """
    Valida si la contraseña cumple con las reglas:
    - Mínimo 8 caracteres
    - Al menos 1 mayúscula
    - Al menos 1 minúscula
    - Al menos 1 número
    - Al menos 1 carácter especial
    """
    resultado = validar_contrasena(payload.password)
    return ValidationResponse(
        valida=resultado["valida"],
        errores=resultado["errores"]
    )

@app.post(
    "/api/v1/validate/email",
    response_model=ValidationResponse,
    tags=["Validaciones"],
    summary="Valida formato de correo electrónico",
)
def validate_email_endpoint(payload: EmailValidationRequest):
    """
    Valida si el correo electrónico tiene un formato sintáctico válido.
    """
    resultado = validar_email(payload.email)
    return ValidationResponse(
        valida=resultado["valida"],
        errores=resultado["errores"]
    )

@app.post(
    "/api/v1/users",
    response_model=UserRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse, "description": "Error de validación o usuario existente"}},
    tags=["Usuarios"],
    summary="Registra un nuevo usuario",
)
def create_user_endpoint(user: UserCreate):
    """
    Registra un usuario en el sistema.
    - Si `es_admin=False`: requiere validación estricta de contraseña y email.
    - Si `es_admin=True`: la validación de contraseña es opcional.
    """
    resultado = registrar_usuario(
        email=user.email,
        password=user.password,
        es_admin=user.es_admin
    )

    if not resultado["exito"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detalle": "No se pudo registrar el usuario por errores de validación.",
                "errores": resultado["errores"]
            }
        )

    creado = resultado["usuario"]
    return UserRegistrationResponse(
        mensaje="Usuario registrado exitosamente.",
        usuario=UserResponse(
            email=creado["email"],
            es_admin=creado["es_admin"],
            has_password=bool(creado["password"])
        )
    )

@app.get(
    "/api/v1/users",
    response_model=List[UserResponse],
    tags=["Usuarios"],
    summary="Lista todos los usuarios registrados",
)
def get_users_endpoint():
    """
    Retorna la lista de usuarios registrados sin exponer contraseñas en texto plano.
    """
    registrados = listar_usuarios()
    return [
        UserResponse(
            email=u["email"],
            es_admin=u["es_admin"],
            has_password=bool(u.get("password"))
        )
        for u in registrados
    ]

def start():
    """
    Punto de entrada para ejecutar el servidor uvicorn.
    """
    uvicorn.run("vibe_coding.api:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    start()
