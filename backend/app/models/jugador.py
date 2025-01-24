from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Jugador(Base):
    __tablename__ = "jugadores"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    apellidos = Column(String, index=True)
    club = Column(String, nullable=True)
    activo = Column(Boolean, default=True)
    campeonato_id = Column(Integer, ForeignKey("campeonatos.id"))
    
    # Relaciones
    campeonato = relationship("Campeonato", back_populates="jugadores")

    # Restricción única compuesta para nombre, apellidos y campeonato
    __table_args__ = (
        UniqueConstraint('nombre', 'apellidos', 'campeonato_id', name='uix_nombre_apellidos_campeonato'),
    )
    

    
   
