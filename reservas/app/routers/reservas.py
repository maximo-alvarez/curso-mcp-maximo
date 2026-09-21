from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_reservas_repo
from app.models.usuario import Usuario
from app.schemas.reserva import ReservaCreate, ReservaOut
from app.services.reservas import (
    FechaPasadaError,
    HorarioInvalidoError,
    HorarioSolapadoError,
    NoAutorizadoError,
    ReservaNoEncontradaError,
    cancelar_reserva,
    crear_reserva,
    listar_reservas,
)

router = APIRouter(prefix="/reservas", tags=["reservas"])


@router.post("/", response_model=ReservaOut, status_code=status.HTTP_201_CREATED)
def endpoint_crear_reserva(
    reserva_in: ReservaCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo=Depends(get_reservas_repo),
):
    try:
        reserva = crear_reserva(
            db,
            usuario_id=current_user.id,
            fecha=reserva_in.fecha,
            hora_inicio=reserva_in.hora_inicio,
            hora_fin=reserva_in.hora_fin,
            repo=repo,
        )
        return reserva
    except (HorarioSolapadoError, HorarioInvalidoError, FechaPasadaError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=list[ReservaOut], status_code=status.HTTP_200_OK)
def endpoint_listar_reservas(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Cantidad máxima de registros a retornar"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo=Depends(get_reservas_repo),
):
    return listar_reservas(
        db,
        usuario_id=current_user.id,
        skip=skip,
        limit=limit,
        repo=repo,
    )


@router.delete("/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT)
def endpoint_cancelar_reserva(
    reserva_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo=Depends(get_reservas_repo),
):
    try:
        cancelar_reserva(
            db,
            usuario_id=current_user.id,
            reserva_id=reserva_id,
            repo=repo,
        )
        return None
    except NoAutorizadoError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ReservaNoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

