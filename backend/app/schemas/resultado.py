from pydantic import BaseModel
from typing import Optional
from app.schemas.jugador import Jugador

class ResultadoBase(BaseModel):
    partida: int
    mesa: int
    jugador: int      # Número del jugador en la mesa (1-4)
    jugador_id: int   # ID del jugador en la base de datos
    PT: int          # Puntos Totales de su pareja
    PV: int          # Puntos Válidos (≤300)
    PC: int          # Puntos Conseguidos (PV propio - PV contrario)
    PG: int          # Partida Ganada (1 si PC > 0, 0 si PC < 0)
    campeonato_id: int

class ResultadoMesaInput(BaseModel):
    campeonato_id: int
    partida: int
    mesa: int
    jugador1_id: int
    jugador2_id: int
    jugador3_id: int
    jugador4_id: int
    puntos_pareja1: int
    puntos_pareja2: int

class Resultado(ResultadoBase):
    id: int
    jugador_data: Optional[Jugador] = None

    class Config:
        from_attributes = True 