from pydantic import BaseModel
from typing import Optional
from .pareja_partida import ParejaPartida as ParejaPartidaSchema

class MesaBase(BaseModel):
    numero_mesa: int
    partida: int
    campeonato_id: int

class MesaCreate(MesaBase):
    pareja_partida1_id: int
    pareja_partida2_id: int

class Mesa(MesaBase):
    id: int
    pareja_partida1: ParejaPartidaSchema
    pareja_partida2: ParejaPartidaSchema

    class Config:
        from_attributes = True 