from sqlalchemy import Column, Integer, String, Date, Boolean
from sqlalchemy.orm import relationship
from ..db.base import Base

class Campeonato(Base):
    __tablename__ = "campeonatos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    fecha_inicio = Column(Date, nullable=False)
    dias_duracion = Column(Integer, nullable=False)
    numero_partidas = Column(Integer, nullable=False)
    activo = Column(Boolean, default=True)
    partida_actual = Column(Integer, default=0)
    finalizado = Column(Boolean, default=False)
    
    # Relaciones
    jugadores = relationship("Jugador", back_populates="campeonato")
    
    