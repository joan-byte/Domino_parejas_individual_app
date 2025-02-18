from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from ..db.base import Base

class Jugador(Base):
    __tablename__ = "jugadores"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(200), nullable=False)
    club = Column(String(100))
    activo = Column(Boolean, default=True)
    campeonato_id = Column(Integer, ForeignKey("campeonatos.id"), primary_key=True)
    
    # Relaciones
    campeonato = relationship("Campeonato", back_populates="jugadores")

    # Restricción única compuesta para nombre, apellidos y campeonato
    __table_args__ = (
        UniqueConstraint('nombre', 'apellidos', 'campeonato_id', name='uix_nombre_apellidos_campeonato'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    )
    
    def __repr__(self):
        return f"<Jugador(id={self.id}, nombre='{self.nombre}', apellidos='{self.apellidos}', club='{self.club}')>"
    

    
   
