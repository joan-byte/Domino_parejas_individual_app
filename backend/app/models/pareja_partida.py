from sqlalchemy import Column, Integer, ForeignKey, ForeignKeyConstraint, UniqueConstraint, and_
from sqlalchemy.orm import relationship
from ..db.base import Base

class ParejaPartida(Base):
    __tablename__ = "parejas_partida"
    
    id = Column(Integer, primary_key=True, index=True)
    partida = Column(Integer, nullable=False)  # Número de partida en el campeonato
    mesa = Column(Integer, nullable=False)     # Número de mesa en la partida
    jugador1_id = Column(Integer, ForeignKey("jugadores.id"), nullable=False)
    jugador2_id = Column(Integer, ForeignKey("jugadores.id"), nullable=True)  # Permitir parejas incompletas
    numero_pareja = Column(Integer, nullable=False)  # 1 o 2 (para identificar la pareja en la mesa)
    campeonato_id = Column(Integer, ForeignKey("campeonatos.id"), nullable=False)
    
    # Relaciones
    jugador1 = relationship("Jugador", foreign_keys=[jugador1_id])
    jugador2 = relationship("Jugador", foreign_keys=[jugador2_id])
    campeonato = relationship("Campeonato")

    # Restricciones
    __table_args__ = (
        # Asegurar que no hay duplicados de parejas en la misma mesa y partida
        UniqueConstraint('partida', 'mesa', 'numero_pareja', 'campeonato_id', 
                        name='uix_pareja_mesa_partida'),
        
        # Asegurar que un jugador no está en más de una pareja en la misma partida como jugador1
        UniqueConstraint('partida', 'jugador1_id', 'campeonato_id',
                        name='uix_jugador1_partida'),
        
        # Asegurar que un jugador no está en más de una pareja en la misma partida como jugador2
        # Esta restricción solo se aplica cuando jugador2_id no es nulo
        UniqueConstraint('partida', 'jugador2_id', 'campeonato_id',
                        name='uix_jugador2_partida'),
        
        # Verificar que los jugadores pertenecen al mismo campeonato
        {'extend_existing': True}
    ) 