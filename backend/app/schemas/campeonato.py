from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class CampeonatoBase(BaseModel):
    nombre: str = Field(..., min_length=1)
    fecha_inicio: date
    dias_duracion: int = Field(gt=0, description="Duración del campeonato en días")
    numero_partidas: int = Field(gt=0, description="Número total de partidas")
    PM: int = Field(default=300, ge=0, description="Puntos Máximos")

class CampeonatoCreate(CampeonatoBase):
    pass

class CampeonatoUpdate(BaseModel):
    nombre: Optional[str] = None
    fecha_inicio: Optional[date] = None
    dias_duracion: Optional[int] = Field(None, gt=0)
    numero_partidas: Optional[int] = Field(None, gt=0)
    PM: Optional[int] = Field(None, ge=0)

class CampeonatoResponse(CampeonatoBase):
    id: int
    activo: bool
    partida_actual: int
    finalizado: bool

    class Config:
        from_attributes = True 