from pydantic import BaseModel

class JugadorBase(BaseModel):
    nombre: str
    apellidos: str
    club: str | None = None

class JugadorCreate(JugadorBase):
    campeonato_id: int

class JugadorUpdate(JugadorBase):
    pass

class JugadorResponse(JugadorBase):
    id: int
    campeonato_id: int
    activo: bool

    class Config:
        from_attributes = True

class Jugador(JugadorBase):
    id: int
    campeonato_id: int
    activo: bool

    class Config:
        from_attributes = True 