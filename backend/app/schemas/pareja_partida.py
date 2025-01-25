from pydantic import BaseModel
from typing import List, Optional
from .jugador import Jugador

class ParejaNueva(BaseModel):
    mesa: int
    jugador1_id: int
    jugador2_id: int
    partida: int

class AsignacionParejas(BaseModel):
    campeonato_id: int
    partida: int
    parejas: List[ParejaNueva]

class ParejaPartidaBase(BaseModel):
    partida: int
    mesa: int
    jugador1_id: int
    jugador2_id: int
    numero_pareja: int  # 1 o 2
    campeonato_id: int

class ParejaPartidaCreate(ParejaPartidaBase):
    pass

class ParejaPartida(ParejaPartidaBase):
    id: int
    jugador1: Optional[Jugador] = None
    jugador2: Optional[Jugador] = None

    class Config:
        from_attributes = True

class SorteoInicial(BaseModel):
    campeonato_id: int
    jugadores: List[int]  # Lista de IDs de jugadores para sortear 