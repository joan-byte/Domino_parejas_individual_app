from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from ..db.base import Base

class ParejaPartida(Base):
    __tablename__ = "pareja_partida"  # Cambiado de "parejas_partida" a "pareja_partida"
    
    id = Column(Integer, primary_key=True, index=True)
    partida = Column(Integer, nullable=False)  # Número de partida en el campeonato
    mesa = Column(Integer, nullable=False)     # Número de mesa en la partida
    jugador1_id = Column(Integer, nullable=False)
    jugador2_id = Column(Integer, nullable=True)  # Permitir parejas incompletas
    numero_pareja = Column(Integer, nullable=False)  # 1 o 2 (para identificar la pareja en la mesa)
    campeonato_id = Column(Integer, ForeignKey("campeonatos.id"), nullable=False)
    
    # Relaciones
    jugador1 = relationship("Jugador", 
                          foreign_keys=[jugador1_id],
                          primaryjoin="and_(ParejaPartida.jugador1_id == Jugador.id, "
                                    "ParejaPartida.campeonato_id == Jugador.campeonato_id)")
    jugador2 = relationship("Jugador", 
                          foreign_keys=[jugador2_id],
                          primaryjoin="and_(ParejaPartida.jugador2_id == Jugador.id, "
                                    "ParejaPartida.campeonato_id == Jugador.campeonato_id)")
    campeonato = relationship("Campeonato")

    # Restricciones según el esquema actual
    __table_args__ = (
        # Asegurar que no hay duplicados de parejas en la misma mesa y partida
        UniqueConstraint('partida', 'mesa', 'numero_pareja', 'campeonato_id', 
                        name='uix_pareja_mesa_partida'),
        
        # Claves foráneas compuestas para jugadores
        ForeignKeyConstraint(
            ['jugador1_id', 'campeonato_id'],
            ['jugadores.id', 'jugadores.campeonato_id'],
            name='fk_jugador1'
        ),
        ForeignKeyConstraint(
            ['jugador2_id', 'campeonato_id'],
            ['jugadores.id', 'jugadores.campeonato_id'],
            name='fk_jugador2',
            # Permitir que jugador2_id sea nulo (parejas incompletas)
            use_alter=True,
            initially="DEFERRED"
        ),
        
        {'extend_existing': True}
    ) 