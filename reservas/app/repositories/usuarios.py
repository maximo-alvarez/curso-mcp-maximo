"""Operaciones de persistencia para usuarios (módulo de funciones sueltas)."""
from sqlalchemy.orm import Session
from app.models.usuario import Usuario


def obtener_por_email(db: Session, email: str) -> Usuario | None:
    """Obtiene un usuario por su email."""
    return db.query(Usuario).filter(Usuario.email == email).first()


def guardar(db: Session, email: str, hashed_password: str) -> Usuario:
    """Guarda un nuevo usuario en la base de datos."""
    usuario = Usuario(email=email, hashed_password=hashed_password)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
