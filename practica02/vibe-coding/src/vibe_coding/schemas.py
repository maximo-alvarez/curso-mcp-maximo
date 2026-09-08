from pydantic import BaseModel, Field
from typing import List

class PasswordValidationRequest(BaseModel):
    password: str = Field(..., description="Contraseña a validar")

class EmailValidationRequest(BaseModel):
    email: str = Field(..., description="Correo electrónico a validar")

class ValidationResponse(BaseModel):
    valida: bool = Field(..., description="Indica si el valor cumple todas las reglas")
    errores: List[str] = Field(default_factory=list, description="Lista de errores encontrados")

class UserCreate(BaseModel):
    email: str = Field(..., description="Correo electrónico del usuario")
    password: str = Field(default="", description="Contraseña del usuario (opcional para administradores)")
    es_admin: bool = Field(default=False, description="Indica si el usuario tiene rol de administrador")

class UserResponse(BaseModel):
    email: str = Field(..., description="Correo electrónico del usuario")
    es_admin: bool = Field(..., description="Indica si el usuario tiene rol de administrador")
    has_password: bool = Field(..., description="Indica si el usuario tiene una contraseña asignada")

class UserRegistrationResponse(BaseModel):
    mensaje: str = Field(..., description="Mensaje de confirmación")
    usuario: UserResponse = Field(..., description="Datos del usuario registrado")

class ErrorResponse(BaseModel):
    detalle: str = Field(..., description="Resumen del error")
    errores: List[str] = Field(default_factory=list, description="Lista detallada de errores de validación")
