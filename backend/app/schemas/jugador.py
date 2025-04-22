from pydantic import BaseModel, Field, validator
import re

class JugadorBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=200)
    club: str = Field(None, max_length=100)
    campeonato_id: int

    @validator('nombre', 'apellidos', 'club')
    def validar_caracteres_especiales(cls, v):
        if v is None:
            return v
        # Permitir letras (incluyendo acentos y ñ), espacios y algunos caracteres especiales
        patron = r'^[a-zA-ZàáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ð\s\'\-\.]+$'
        if not re.match(patron, v, re.UNICODE):
            raise ValueError('El campo solo puede contener letras (incluyendo acentos), espacios y algunos caracteres especiales (. - \')')
        # Verificar que no haya espacios múltiples consecutivos y que no empiece ni termine con espacio
        v = ' '.join(v.split())
        return v

class JugadorCreate(JugadorBase):
    activo: bool = True

class JugadorUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=2, max_length=100)
    apellidos: str | None = Field(None, min_length=2, max_length=200)
    club: str | None = Field(None, max_length=100)
    activo: bool | None = None

    @validator('nombre', 'apellidos', 'club')
    def validar_caracteres_especiales(cls, v):
        if v is None:
            return v
        patron = r'^[a-zA-ZàáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ð\s\'\-\.]+$'
        if not re.match(patron, v, re.UNICODE):
            raise ValueError('El campo solo puede contener letras (incluyendo acentos), espacios y algunos caracteres especiales (. - \')')
        # Verificar que no haya espacios múltiples consecutivos y que no empiece ni termine con espacio
        v = ' '.join(v.split())
        return v

class JugadorResponse(JugadorBase):
    id: int
    activo: bool

    class Config:
        from_attributes = True

class Jugador(JugadorBase):
    id: int
    campeonato_id: int
    activo: bool

    class Config:
        from_attributes = True 