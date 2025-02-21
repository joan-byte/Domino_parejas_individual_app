from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from ..db.base import Base

class Resultado(Base):
    __tablename__ = "resultados"
    
    id = Column(Integer, primary_key=True, index=True)
    partida = Column(Integer, nullable=False)
    mesa = Column(Integer, nullable=False)
    jugador = Column(Integer, nullable=False)  # 1, 2, 3 o 4 (posición del jugador en la mesa)
    jugador_id = Column(Integer, nullable=False)
    pareja = Column(Integer)  # 1 o 2 (número de la pareja en la mesa)
    PT = Column(Integer, nullable=False)  # Puntos Totales
    PV = Column(Integer, nullable=False)  # Puntos Válidos (limitado por PM del campeonato)
    PC = Column(Integer, nullable=False)  # Puntos Conseguidos (PV propio - PV contrario)
    PG = Column(Integer, nullable=False)  # Partida Ganada (1 si PC > 0, 0 si PC < 0)
    MG = Column(Integer, nullable=False)  # Manos Ganadas (se introduce junto con PT)
    campeonato_id = Column(Integer, ForeignKey("campeonatos.id"), nullable=False)
    
    # Relaciones
    jugador_data = relationship("Jugador", 
                              foreign_keys=[jugador_id, campeonato_id],
                              primaryjoin="and_(Resultado.jugador_id == Jugador.id, "
                                        "Resultado.campeonato_id == Jugador.campeonato_id)",
                              overlaps="resultados")
    campeonato = relationship("Campeonato", back_populates="resultados", overlaps="jugador_data")

    # Restricciones
    __table_args__ = (
        ForeignKeyConstraint(
            ['jugador_id', 'campeonato_id'],
            ['jugadores.id', 'jugadores.campeonato_id']
        ),
        # Asegurar que no hay duplicados de resultados para un jugador en una partida
        UniqueConstraint('partida', 'jugador_id', 'campeonato_id',
                        name='uix_jugador_partida_resultado'),
        # Asegurar que no hay duplicados de posición en una mesa
        UniqueConstraint('partida', 'mesa', 'jugador', 'campeonato_id',
                        name='uix_posicion_mesa_partida')
    ) 