from pydantic import BaseModel
from typing import Optional

class JugadorBase(BaseModel):
    nombre: str
    apellido: str
    club: Optional[str] = None
    activo: Optional[bool] = True

class JugadorCreate(JugadorBase):
    campeonato_id: Optional[int] = None

class JugadorUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    club: Optional[str] = None
    activo: Optional[bool] = None
    campeonato_id: Optional[int] = None

class JugadorResponse(JugadorBase):
    id: int
    campeonato_id: Optional[int] = None
    
    class Config:
        from_attributes = True 