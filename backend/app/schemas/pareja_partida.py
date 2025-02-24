from pydantic import BaseModel
from typing import List, Optional
from .jugador import Jugador

class ParejaNueva(BaseModel):
    mesa: int
    jugador1_id: int
    jugador2_id: Optional[int] = None
    partida: int

class AsignacionParejas(BaseModel):
    campeonato_id: int
    partida: int
    parejas: List[ParejaNueva]

class ParejaPartidaBase(BaseModel):
    partida: int
    mesa: int
    jugador1_id: int
    jugador2_id: Optional[int] = None
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

class SiguientePartidaResponse(BaseModel):
    parejas: List[ParejaPartida]
    jugadores_sin_asignar: List[int]
    mesas_formadas: int

    class Config:
        from_attributes = True 