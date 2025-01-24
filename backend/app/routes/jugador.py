from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from app.db.base import get_db
from app.models.jugador import Jugador
from app.schemas.jugador import JugadorCreate, JugadorResponse, JugadorUpdate

router = APIRouter(
    prefix="/api/jugadores",
    tags=["jugadores"]
)

@router.post("/", response_model=JugadorResponse)
async def create_jugador(jugador: JugadorCreate, db: Session = Depends(get_db)):
    """Crear un nuevo jugador"""
    # Verificar si ya existe un jugador con el mismo nombre y apellidos en el mismo campeonato
    existing_jugador = db.query(Jugador).filter(
        and_(
            Jugador.nombre == jugador.nombre,
            Jugador.apellidos == jugador.apellidos,
            Jugador.campeonato_id == jugador.campeonato_id
        )
    ).first()
    
    if existing_jugador:
        raise HTTPException(
            status_code=400,
            detail=f"El jugador {jugador.nombre} {jugador.apellidos} ya está inscrito en este campeonato"
        )
    
    # Crear el jugador con los campos del esquema y establecer activo=True
    jugador_data = jugador.dict()
    jugador_data['activo'] = True  # Forzar activo=True al crear
    db_jugador = Jugador(**jugador_data)
    db.add(db_jugador)
    db.commit()
    db.refresh(db_jugador)
    return db_jugador

@router.get("/", response_model=List[JugadorResponse])
def read_jugadores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de jugadores"""
    jugadores = db.query(Jugador).offset(skip).limit(limit).all()
    return jugadores

@router.get("/{jugador_id}", response_model=JugadorResponse)
def read_jugador(jugador_id: int, db: Session = Depends(get_db)):
    """Obtener un jugador específico"""
    jugador = db.query(Jugador).filter(Jugador.id == jugador_id).first()
    if jugador is None:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    return jugador

@router.put("/{jugador_id}", response_model=JugadorResponse)
def update_jugador(jugador_id: int, jugador: JugadorUpdate, db: Session = Depends(get_db)):
    """Actualizar un jugador"""
    db_jugador = db.query(Jugador).filter(Jugador.id == jugador_id).first()
    if db_jugador is None:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    # Si se está actualizando nombre o apellidos, verificar que no exista otro jugador con esa combinación
    if (jugador.nombre is not None or jugador.apellidos is not None):
        nuevo_nombre = jugador.nombre if jugador.nombre is not None else db_jugador.nombre
        nuevo_apellidos = jugador.apellidos if jugador.apellidos is not None else db_jugador.apellidos
        
        existing_jugador = db.query(Jugador).filter(
            and_(
                Jugador.nombre == nuevo_nombre,
                Jugador.apellidos == nuevo_apellidos,
                Jugador.campeonato_id == db_jugador.campeonato_id,
                Jugador.id != jugador_id
            )
        ).first()
        
        if existing_jugador:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe otro jugador con el nombre {nuevo_nombre} {nuevo_apellidos} en este campeonato"
            )
    
    for key, value in jugador.dict(exclude_unset=True).items():
        setattr(db_jugador, key, value)
    
    db.commit()
    db.refresh(db_jugador)
    return db_jugador

@router.delete("/{jugador_id}")
def delete_jugador(jugador_id: int, db: Session = Depends(get_db)):
    """Eliminar un jugador"""
    db_jugador = db.query(Jugador).filter(Jugador.id == jugador_id).first()
    if db_jugador is None:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    db.delete(db_jugador)
    db.commit()
    return {"message": "Jugador eliminado"}

@router.get("/campeonato/{campeonato_id}", response_model=List[JugadorResponse])
async def get_jugadores_by_campeonato(campeonato_id: int, db: Session = Depends(get_db)):
    """Obtener jugadores de un campeonato específico"""
    jugadores = db.query(Jugador).filter(Jugador.campeonato_id == campeonato_id).all()
    return jugadores

@router.put("/{jugador_id}/toggle-activo", response_model=JugadorResponse)
async def toggle_jugador_activo(jugador_id: int, db: Session = Depends(get_db)):
    jugador = db.query(Jugador).filter(Jugador.id == jugador_id).first()
    if not jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    jugador.activo = not jugador.activo
    db.commit()
    db.refresh(jugador)
    return jugador
    