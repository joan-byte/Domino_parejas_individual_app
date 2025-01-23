from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from ..db.base import Base

class Jugador(Base):
    __tablename__ = "jugadores"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    club = Column(String, nullable=True)
    activo = Column(Boolean, default=True)
    campeonato_id = Column(Integer, ForeignKey("campeonatos.id"), nullable=True)
    
    # Relaciones
    campeonato = relationship("Campeonato", back_populates="jugadores")

    # Restricción única compuesta para nombre y apellido
    __table_args__ = (
        UniqueConstraint('nombre', 'apellido', name='uix_nombre_apellido'),
    )
    

    
   
