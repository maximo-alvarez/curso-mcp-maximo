from sqlalchemy import Column, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    fecha = Column(String(10), nullable=False)
    hora_inicio = Column(String(5), nullable=False)
    hora_fin = Column(String(5), nullable=False)
    estado = Column(String(20), nullable=False, default="ACTIVA")

    usuario = relationship("Usuario", back_populates="reservas")

    __table_args__ = (
        Index("ix_reservas_fecha_estado", "fecha", "estado"),
    )
