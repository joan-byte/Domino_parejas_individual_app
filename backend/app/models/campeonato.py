from sqlalchemy import Column, Integer, String, Date, Boolean
from sqlalchemy.orm import relationship
from ..db.base import Base
from datetime import date

class Campeonato(Base):
    __tablename__ = "campeonatos"
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    fecha_inicio = Column(Date)
    dias_duracion = Column(Integer)
    numero_partidas = Column(Integer)
    PM = Column(Integer, default=300)
    activo = Column(Boolean, default=True)
    partida_actual = Column(Integer, default=0)
    finalizado = Column(Boolean, default=False)
    
    # Relaciones
    jugadores = relationship("Jugador", back_populates="campeonato", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        if 'fecha_inicio' in kwargs and isinstance(kwargs['fecha_inicio'], str):
            kwargs['fecha_inicio'] = date.fromisoformat(kwargs['fecha_inicio'])
        super().__init__(**kwargs)
    
    