from sqlalchemy import Column, Integer, String, Date, Boolean
from sqlalchemy.orm import relationship
from ..db.base import Base
from datetime import date

class Campeonato(Base):
    __tablename__ = "campeonatos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    dias_duracion = Column(Integer, nullable=False)
    numero_partidas = Column(Integer, nullable=False)
    PM = Column(Integer, nullable=False)  # Puntos Máximos
    activo = Column(Boolean, default=True)
    partida_actual = Column(Integer, default=0)
    finalizado = Column(Boolean, default=False)
    
    # Relaciones
    jugadores = relationship("Jugador", back_populates="campeonato", cascade="all, delete-orphan")
    resultados = relationship("Resultado", back_populates="campeonato", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        if 'fecha_inicio' in kwargs and isinstance(kwargs['fecha_inicio'], str):
            kwargs['fecha_inicio'] = date.fromisoformat(kwargs['fecha_inicio'])
        super().__init__(**kwargs)
    
    