from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_db
from app.models.mesa import Mesa
from app.schemas.mesa import MesaCreate, Mesa as MesaSchema

router = APIRouter()

@router.post("/mesas/", response_model=MesaSchema)
def create_mesa(mesa: MesaCreate, db: Session = Depends(get_db)):
    # Obtener el último número de mesa para esta partida y campeonato
    ultimo_numero = db.query(Mesa).filter(
        Mesa.partida == mesa.partida,
        Mesa.campeonato_id == mesa.campeonato_id
    ).count()
    
    # Crear la nueva mesa con número incrementado
    db_mesa = Mesa(
        numero_mesa=ultimo_numero + 1,
        partida=mesa.partida,
        pareja1_id=mesa.pareja1_id,
        pareja2_id=mesa.pareja2_id,
        campeonato_id=mesa.campeonato_id
    )
    
    db.add(db_mesa)
    db.commit()
    db.refresh(db_mesa)
    return db_mesa

@router.get("/mesas/", response_model=List[MesaSchema])
def read_mesas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    mesas = db.query(Mesa).offset(skip).limit(limit).all()
    return mesas

@router.get("/mesas/{mesa_id}", response_model=MesaSchema)
def read_mesa(mesa_id: int, db: Session = Depends(get_db)):
    mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if mesa is None:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")
    return mesa

@router.get("/mesas/campeonato/{campeonato_id}/partida/{partida}", response_model=List[MesaSchema])
def read_mesas_by_campeonato_partida(campeonato_id: int, partida: int, db: Session = Depends(get_db)):
    mesas = db.query(Mesa).filter(
        Mesa.campeonato_id == campeonato_id,
        Mesa.partida == partida
    ).order_by(Mesa.numero_mesa).all()
    return mesas 