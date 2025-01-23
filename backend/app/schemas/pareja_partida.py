from pydantic import BaseModel
from typing import List
from .jugador import JugadorBase

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
    jugador1: JugadorBase
    jugador2: JugadorBase

    class Config:
        from_attributes = True

class SorteoInicial(BaseModel):
    campeonato_id: int
    jugadores: List[int]  # Lista de IDs de jugadores para sortear 