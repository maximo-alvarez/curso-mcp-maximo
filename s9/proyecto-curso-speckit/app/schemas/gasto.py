from pydantic import BaseModel, ConfigDict


class GastoCreate(BaseModel):
    descripcion: str
    monto: float
    categoria: str


class GastoResponse(BaseModel):
    id: int
    descripcion: str
    monto: float
    categoria: str

    model_config = ConfigDict(from_attributes=True)
