from pydantic import BaseModel
from typing import Optional
from .jugador import JugadorBase

class ResultadoBase(BaseModel):
    partida: int
    mesa: int
    jugador: int  # 1, 2, 3 o 4
    jugador_id: int
    pareja: int  # 1 o 2
    PT: int      # Puntos Totales
    PV: int      # Puntos Válidos (≤300)
    PC: int      # Puntos Conseguidos
    PG: int      # Partida Ganada
    campeonato_id: int

class ResultadoMesaInput(BaseModel):
    partida: int
    mesa: int
    campeonato_id: int
    # Jugadores
    jugador1_id: int  # Jugador 1 de la mesa
    jugador2_id: int  # Jugador 2 de la mesa
    jugador3_id: int  # Jugador 3 de la mesa
    jugador4_id: int  # Jugador 4 de la mesa
    # Puntos totales de cada pareja
    puntos_pareja1: int  # Puntos de la pareja 1 (jugadores 1 y 2)
    puntos_pareja2: int  # Puntos de la pareja 2 (jugadores 3 y 4)

class ResultadoCreate(ResultadoBase):
    pass

class Resultado(BaseModel):
    id: int
    partida: int
    mesa: int
    jugador: int      # Número del jugador en la mesa (1-4)
    jugador_id: int   # ID del jugador en la base de datos
    PT: int          # Puntos Totales de su pareja
    PV: int          # Puntos Válidos (≤300)
    PC: int          # Puntos Conseguidos (PV propio - PV contrario)
    PG: int          # Partida Ganada (1 si PC > 0, 0 si PC < 0)
    campeonato_id: int
    jugador_rel: JugadorBase

    class Config:
        from_attributes = True 