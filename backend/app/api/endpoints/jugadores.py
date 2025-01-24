from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.jugador import Jugador
from app.schemas.jugador import JugadorCreate, JugadorUpdate, Jugador as JugadorSchema

router = APIRouter()

@router.post("/", response_model=JugadorSchema)
def create_jugador(jugador: JugadorCreate, db: Session = Depends(get_db)):
    db_jugador = Jugador(
        nombre=jugador.nombre,
        apellidos=jugador.apellidos,
        email=jugador.email,
        telefono=jugador.telefono,
        campeonato_id=jugador.campeonato_id
    )
    db.add(db_jugador)
    db.commit()
    db.refresh(db_jugador)
    return db_jugador

@router.get("/{jugador_id}", response_model=JugadorSchema)
def read_jugador(jugador_id: int, db: Session = Depends(get_db)):
    jugador = db.query(Jugador).filter(Jugador.id == jugador_id).first()
    if jugador is None:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    return jugador

@router.get("/campeonato/{campeonato_id}", response_model=List[JugadorSchema])
def read_jugadores_by_campeonato(campeonato_id: int, db: Session = Depends(get_db)):
    jugadores = db.query(Jugador).filter(Jugador.campeonato_id == campeonato_id).all()
    return jugadores

@router.put("/{jugador_id}", response_model=JugadorSchema)
def update_jugador(jugador_id: int, jugador: JugadorUpdate, db: Session = Depends(get_db)):
    db_jugador = db.query(Jugador).filter(Jugador.id == jugador_id).first()
    if db_jugador is None:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    for field, value in jugador.dict().items():
        setattr(db_jugador, field, value)
    
    db.commit()
    db.refresh(db_jugador)
    return db_jugador

@router.delete("/{jugador_id}")
def delete_jugador(jugador_id: int, db: Session = Depends(get_db)):
    jugador = db.query(Jugador).filter(Jugador.id == jugador_id).first()
    if jugador is None:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    db.delete(jugador)
    db.commit()
    return {"message": "Jugador eliminado correctamente"} 