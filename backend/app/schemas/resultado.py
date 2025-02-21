from pydantic import BaseModel
from typing import Optional
from app.schemas.jugador import Jugador

class ResultadoBase(BaseModel):
    partida: int
    mesa: int
    jugador: int      # Número del jugador en la mesa (1-4)
    jugador_id: int   # ID del jugador en la base de datos
    pareja: int      # 1 o 2 (número de la pareja en la mesa)
    PT: int          # Puntos Totales de su pareja
    PV: int          # Puntos Válidos (limitado por PM del campeonato)
    PC: int          # Puntos Conseguidos (PV propio - PV contrario)
    PG: int          # Partida Ganada (1 si PC > 0, 0 si PC < 0)
    MG: int          # Manos Ganadas
    campeonato_id: int

class ResultadoMesaInput(BaseModel):
    campeonato_id: int
    partida: int
    mesa: int
    # Jugadores de la primera pareja (siempre presentes)
    jugador1_id: int
    jugador2_id: int
    # Jugadores restantes (pueden ser 0, 1 o 2)
    jugador3_id: Optional[int] = None  # Tercer jugador (puede ser de la segunda pareja)
    jugador4_id: Optional[int] = None  # Cuarto jugador (solo si hay segunda pareja completa)
    # Puntos por jugador o pareja según el caso
    puntos_pareja1: int  # Puntos de la primera pareja (siempre presente)
    puntos_jugador3: Optional[int] = None  # Puntos del tercer jugador si existe
    puntos_jugador4: Optional[int] = None  # Puntos del cuarto jugador si existe
    # Manos ganadas
    mesas_ganadas_pareja1: int  # Manos ganadas primera pareja
    mesas_ganadas_jugador3: Optional[int] = None  # Manos ganadas tercer jugador
    mesas_ganadas_jugador4: Optional[int] = None  # Manos ganadas cuarto jugador

class ResultadoCreate(ResultadoBase):
    pass

class Resultado(ResultadoBase):
    id: int
    jugador_data: Optional[Jugador] = None

    class Config:
        from_attributes = True 