from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class CampeonatoBase(BaseModel):
    nombre: str
    fecha_inicio: date
    dias_duracion: int = Field(gt=0, description="Duración del campeonato en días")
    numero_partidas: int = Field(gt=0, description="Número total de partidas")
    PM: int = Field(default=300, description="Puntos Máximos")

class CampeonatoCreate(CampeonatoBase):
    pass

class CampeonatoUpdate(BaseModel):
    nombre: Optional[str] = None
    fecha_inicio: Optional[date] = None
    dias_duracion: Optional[int] = Field(None, gt=0, description="Duración del campeonato en días")
    numero_partidas: Optional[int] = Field(None, gt=0, description="Número total de partidas")
    PM: Optional[int] = Field(None, description="Puntos Máximos")

class CampeonatoResponse(CampeonatoBase):
    id: int
    activo: bool
    partida_actual: int

    class Config:
        from_attributes = True 