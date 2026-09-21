from pydantic import BaseModel, ConfigDict, Field


class ReservaBase(BaseModel):
    fecha: str = Field(..., description="Fecha de la reserva en formato YYYY-MM-DD")
    hora_inicio: str = Field(..., description="Hora de inicio en formato HH:MM")
    hora_fin: str = Field(..., description="Hora de fin en formato HH:MM")


class ReservaCreate(ReservaBase):
    pass


class ReservaOut(ReservaBase):
    id: int
    usuario_id: int
    estado: str

    model_config = ConfigDict(from_attributes=True)
