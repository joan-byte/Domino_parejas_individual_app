from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..db.base import Base
from .jugador import Jugador

class Resultado(Base):
    __tablename__ = "resultados"
    
    id = Column(Integer, primary_key=True, index=True)
    partida = Column(Integer)
    mesa = Column(Integer)
    jugador = Column(Integer)  # 1, 2, 3 o 4 (posición del jugador en la mesa)
    jugador_id = Column(Integer, ForeignKey("jugadores.id"))
    pareja = Column(Integer)  # 1 o 2 (número de la pareja en la mesa)
    PT = Column(Integer)  # Puntos Totales
    PV = Column(Integer)  # Puntos Válidos (≤300)
    PC = Column(Integer)  # Puntos Conseguidos (PV propio - PV contrario)
    PG = Column(Integer)  # Partida Ganada (1 si PC > 0, 0 si PC < 0)
    MG = Column(Integer)  # Manos Ganadas (se introduce junto con PT)
    campeonato_id = Column(Integer, ForeignKey("campeonatos.id"))
    
    # Relaciones
    jugador_data = relationship("Jugador", backref="resultados")
    campeonato = relationship("Campeonato") 