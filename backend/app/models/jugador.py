from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..db.base import Base

class Jugador(Base):
    __tablename__ = "jugadores"
    
    id = Column(Integer, primary_key=True)
    campeonato_id = Column(Integer, ForeignKey("campeonatos.id"), primary_key=True)
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(200), nullable=False)
    club = Column(String(100))
    activo = Column(Boolean, default=True)
    
    # Relaciones
    campeonato = relationship("Campeonato", back_populates="jugadores")
    
    def __repr__(self):
        return f"<Jugador(id={self.id}, nombre='{self.nombre}', apellidos='{self.apellidos}', club='{self.club}')>"
    

    
   
