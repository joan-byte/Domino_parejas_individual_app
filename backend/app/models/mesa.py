from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..db.base import Base

class Mesa(Base):
    __tablename__ = "mesas"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_mesa = Column(Integer)  # Este empezará en 1 para cada partida
    partida = Column(Integer)
    pareja_partida1_id = Column(Integer, ForeignKey("parejas_partida.id"), nullable=False)
    pareja_partida2_id = Column(Integer, ForeignKey("parejas_partida.id"), nullable=True)  # Nullable para la última mesa
    campeonato_id = Column(Integer, ForeignKey("campeonatos.id"))
    
    # Relaciones
    pareja_partida1 = relationship("ParejaPartida", foreign_keys=[pareja_partida1_id])
    pareja_partida2 = relationship("ParejaPartida", foreign_keys=[pareja_partida2_id])
    campeonato = relationship("Campeonato") 