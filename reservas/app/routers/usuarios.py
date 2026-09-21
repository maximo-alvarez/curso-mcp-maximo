from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.usuario import Token, UsuarioCreate, UsuarioOut
from app.services.usuarios import (
    CredencialesInvalidasError,
    EmailYaRegistradoError,
    autenticar_usuario,
    registrar_usuario,
)

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario_in: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        usuario = registrar_usuario(db, email=usuario_in.email, password=usuario_in.password)
        return usuario
    except EmailYaRegistradoError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
def login_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        token_data = autenticar_usuario(db, email=form_data.username, password=form_data.password)
        return token_data
    except CredencialesInvalidasError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
