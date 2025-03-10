from pydantic import BaseModel
from typing import List, Optional
from .jugador import Jugador

class ParejaNueva(BaseModel):
    mesa: int
    jugador1_id: int
    jugador2_id: Optional[int] = None
    partida: int

class ParejaPartidaBase(BaseModel):
    partida: int
    mesa: int
    jugador1_id: int
    jugador2_id: Optional[int] = None
    numero_pareja: int  # 1 o 2
    campeonato_id: int

class ParejaPartidaCreate(ParejaPartidaBase):
    pass

class ParejaPartidaSchema(ParejaPartidaBase):
    id: int
    jugador1: Optional[Jugador] = None
    jugador2: Optional[Jugador] = None

    class Config:
        from_attributes = True

class AsignacionParejas(BaseModel):
    campeonato_id: int
    parejas: List[ParejaNueva]

class SorteoInicial(BaseModel):
    campeonato_id: int
    jugadores: List[int]  # Lista de IDs de jugadores para sortear

class SiguientePartidaResponse(BaseModel):
    mensaje: str
    nueva_partida: int

class JugadorAsignadoSchema(BaseModel):
    id: int
    nombre: str
    apellidos: str
    club: Optional[str] = None
    mesa: int
    numero_pareja: int

class MesaSchema(BaseModel):
    numeroMesa: int
    pareja1: Optional[ParejaPartidaSchema] = None
    pareja2: Optional[ParejaPartidaSchema] = None 