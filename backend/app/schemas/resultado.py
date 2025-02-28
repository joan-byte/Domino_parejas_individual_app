from pydantic import BaseModel, validator
from typing import Optional
from app.schemas.jugador import Jugador

class ResultadoBase(BaseModel):
    partida: int
    mesa: int
    jugador: int      # Número del jugador en la mesa (1-4)
    jugador_id: int   # ID del jugador en la base de datos
    pareja: int      # 1 o 2 (número de la pareja en la mesa)
    PT: int          # Puntos Totales de su pareja
    PV: int          # Puntos Válidos (limitado por PM del campeonato)
    PC: int          # Puntos Conseguidos (PV propio - PV contrario)
    PG: int          # Partida Ganada (1 si PC > 0, 0 si PC < 0)
    MG: int          # Manos Ganadas
    campeonato_id: int

class ResultadoMesaInput(BaseModel):
    campeonato_id: int
    partida: int
    mesa: int
    es_ultima_mesa: bool  # Nuevo campo para indicar si es la última mesa
    # Jugadores de la primera pareja
    jugador1_id: int
    jugador2_id: Optional[int] = None
    # Jugadores de la segunda pareja
    jugador3_id: Optional[int] = None
    jugador4_id: Optional[int] = None
    # Puntos por pareja
    puntos_pareja1: int
    puntos_pareja2: Optional[int] = None
    # Manos ganadas
    manos_ganadas_pareja1: int
    manos_ganadas_pareja2: Optional[int] = None

    @validator('jugador2_id', 'jugador3_id', 'jugador4_id')
    def validar_jugadores_mesa_normal(cls, v, values):
        if 'es_ultima_mesa' in values and not values['es_ultima_mesa']:
            # Si no es la última mesa, todos los jugadores son obligatorios
            if v is None:
                raise ValueError('Todas las mesas excepto la última deben tener 4 jugadores')
        return v

    @validator('jugador1_id')
    def validar_jugador1_obligatorio(cls, v):
        if v is None:
            raise ValueError('El primer jugador es obligatorio en todas las mesas')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "campeonato_id": 1,
                "partida": 1,
                "mesa": 1,
                "es_ultima_mesa": False,
                "jugador1_id": 1,
                "jugador2_id": 2,
                "jugador3_id": 3,
                "jugador4_id": 4,
                "puntos_pareja1": 100,
                "puntos_pareja2": 80,
                "manos_ganadas_pareja1": 2,
                "manos_ganadas_pareja2": 1
            }
        }

class ResultadoCreate(ResultadoBase):
    pass

class Resultado(ResultadoBase):
    id: int
    jugador_data: Optional[Jugador] = None

    class Config:
        from_attributes = True 