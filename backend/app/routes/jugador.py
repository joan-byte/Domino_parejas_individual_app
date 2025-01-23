from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from app.db.base import get_db
from app.models.jugador import Jugador
from app.schemas.jugador import JugadorCreate, JugadorResponse, JugadorUpdate

router = APIRouter()

@router.post("/jugadores/", response_model=JugadorResponse)
def create_jugador(jugador: JugadorCreate, db: Session = Depends(get_db)):
    """Crear un nuevo jugador"""
    # Verificar si ya existe un jugador con el mismo nombre y apellido
    existing_jugador = db.query(Jugador).filter(
        and_(
            Jugador.nombre == jugador.nombre,
            Jugador.apellido == jugador.apellido
        )
    ).first()
    
    if existing_jugador:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un jugador con el nombre {jugador.nombre} {jugador.apellido}"
        )
    
    db_jugador = Jugador(**jugador.dict())
    db.add(db_jugador)
    db.commit()
    db.refresh(db_jugador)
    return db_jugador

@router.get("/jugadores/", response_model=List[JugadorResponse])
def read_jugadores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de jugadores"""
    jugadores = db.query(Jugador).offset(skip).limit(limit).all()
    return jugadores

@router.get("/jugadores/{jugador_id}", response_model=JugadorResponse)
def read_jugador(jugador_id: int, db: Session = Depends(get_db)):
    """Obtener un jugador específico"""
    jugador = db.query(Jugador).filter(Jugador.id == jugador_id).first()
    if jugador is None:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    return jugador

@router.put("/jugadores/{jugador_id}", response_model=JugadorResponse)
def update_jugador(jugador_id: int, jugador: JugadorUpdate, db: Session = Depends(get_db)):
    """Actualizar un jugador"""
    db_jugador = db.query(Jugador).filter(Jugador.id == jugador_id).first()
    if db_jugador is None:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    # Si se está actualizando nombre o apellido, verificar que no exista otro jugador con esa combinación
    if (jugador.nombre is not None or jugador.apellido is not None):
        nuevo_nombre = jugador.nombre if jugador.nombre is not None else db_jugador.nombre
        nuevo_apellido = jugador.apellido if jugador.apellido is not None else db_jugador.apellido
        
        existing_jugador = db.query(Jugador).filter(
            and_(
                Jugador.nombre == nuevo_nombre,
                Jugador.apellido == nuevo_apellido,
                Jugador.id != jugador_id
            )
        ).first()
        
        if existing_jugador:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un jugador con el nombre {nuevo_nombre} {nuevo_apellido}"
            )
    
    for key, value in jugador.dict(exclude_unset=True).items():
        setattr(db_jugador, key, value)
    
    db.commit()
    db.refresh(db_jugador)
    return db_jugador

@router.delete("/jugadores/{jugador_id}")
def delete_jugador(jugador_id: int, db: Session = Depends(get_db)):
    """Eliminar un jugador"""
    db_jugador = db.query(Jugador).filter(Jugador.id == jugador_id).first()
    if db_jugador is None:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    db.delete(db_jugador)
    db.commit()
    return {"message": "Jugador eliminado"}

@router.get("/jugadores/campeonato/{campeonato_id}", response_model=List[JugadorResponse])
def read_jugadores_by_campeonato(campeonato_id: int, db: Session = Depends(get_db)):
    """Obtener jugadores de un campeonato específico"""
    jugadores = db.query(Jugador).filter(Jugador.campeonato_id == campeonato_id).all()
    return jugadores
    