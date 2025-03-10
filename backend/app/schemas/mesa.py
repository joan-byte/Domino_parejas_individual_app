from pydantic import BaseModel
from typing import Optional
from .pareja_partida import ParejaPartidaSchema

class MesaBase(BaseModel):
    numero_mesa: int
    partida: int
    campeonato_id: int

class MesaCreate(MesaBase):
    pareja_partida1_id: int
    pareja_partida2_id: Optional[int] = None  # Opcional para la última mesa

class Mesa(MesaBase):
    id: int
    pareja_partida1: ParejaPartidaSchema
    pareja_partida2: Optional[ParejaPartidaSchema] = None  # Opcional para la última mesa

    class Config:
        from_attributes = True 