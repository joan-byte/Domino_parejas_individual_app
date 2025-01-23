from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..db.base import Base

class ParejaPartida(Base):
    __tablename__ = "parejas_partida"
    
    id = Column(Integer, primary_key=True, index=True)
    partida = Column(Integer)
    mesa = Column(Integer)
    jugador1_id = Column(Integer, ForeignKey("jugadores.id"))
    jugador2_id = Column(Integer, ForeignKey("jugadores.id"))
    numero_pareja = Column(Integer)  # 1 o 2 (para identificar la pareja en la mesa)
    campeonato_id = Column(Integer, ForeignKey("campeonatos.id"))
    
    # Relaciones
    jugador1 = relationship("Jugador", foreign_keys=[jugador1_id])
    jugador2 = relationship("Jugador", foreign_keys=[jugador2_id])
    campeonato = relationship("Campeonato") 