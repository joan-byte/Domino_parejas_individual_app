from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.db.base import get_db
from app.models.campeonato import Campeonato
from app.schemas.campeonato import CampeonatoCreate, CampeonatoResponse, CampeonatoUpdate
from app.models.resultado import Resultado
from app.models.pareja_partida import ParejaPartida
from app.models.jugador import Jugador
from sqlalchemy.sql import text
from sqlalchemy import and_

router = APIRouter(
    prefix="/campeonatos",
    tags=["campeonatos"]
)

@router.get("/", response_model=List[CampeonatoResponse])
async def read_campeonatos(db: Session = Depends(get_db)):
    """Obtener lista de todos los campeonatos registrados en el sistema."""
    return db.query(Campeonato).all()

@router.post("/", response_model=CampeonatoResponse)
def create_campeonato(campeonato: CampeonatoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo campeonato"""
    try:
        print(f"Intentando crear campeonato: {campeonato.dict()}")
        
        # Verificar si ya existe un campeonato con el mismo nombre y fecha usando SQLAlchemy
        existing_campeonato = db.query(Campeonato).filter(
            and_(
                Campeonato.nombre == campeonato.nombre,
                Campeonato.fecha_inicio == campeonato.fecha_inicio
            )
        ).first()
        
        if existing_campeonato:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un campeonato con el nombre '{campeonato.nombre}' en la fecha {campeonato.fecha_inicio}"
            )

        # Crear el nuevo campeonato usando SQLAlchemy
        db_campeonato = Campeonato(
            nombre=campeonato.nombre,
            fecha_inicio=campeonato.fecha_inicio,
            dias_duracion=campeonato.dias_duracion,
            numero_partidas=campeonato.numero_partidas,
            PM=campeonato.PM,
            activo=True,
            partida_actual=0,
            finalizado=False
        )
        
        db.add(db_campeonato)
        db.commit()
        db.refresh(db_campeonato)
        
        return db_campeonato
        
    except Exception as e:
        db.rollback()
        print(f"Error inesperado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/{campeonato_id}", response_model=CampeonatoResponse)
async def read_campeonato(campeonato_id: int, db: Session = Depends(get_db)):
    """Obtener un campeonato específico por ID"""
    campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
    if campeonato is None:
        raise HTTPException(status_code=404, detail="Campeonato no encontrado")
    return campeonato

@router.put("/{campeonato_id}", response_model=CampeonatoResponse)
async def update_campeonato(campeonato_id: int, campeonato: CampeonatoUpdate, db: Session = Depends(get_db)):
    """Actualizar un campeonato existente"""
    db_campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
    if db_campeonato is None:
        raise HTTPException(status_code=404, detail="Campeonato no encontrado")
    
    for key, value in campeonato.dict(exclude_unset=True).items():
        setattr(db_campeonato, key, value)
    
    db.commit()
    db.refresh(db_campeonato)
    return db_campeonato

@router.delete("/{campeonato_id}", status_code=204)
async def delete_campeonato(campeonato_id: int, db: Session = Depends(get_db)):
    """Elimina un campeonato y todas sus entidades relacionadas"""
    try:
        db_campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
        if db_campeonato is None:
            raise HTTPException(status_code=404, detail="Campeonato no encontrado")
        
        db.query(Resultado).filter(Resultado.campeonato_id == campeonato_id).delete()
        db.query(ParejaPartida).filter(ParejaPartida.campeonato_id == campeonato_id).delete()
        db.query(Jugador).filter(Jugador.campeonato_id == campeonato_id).delete()
        db.delete(db_campeonato)
        db.commit()
        
        return {"message": "Campeonato eliminado"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{campeonato_id}/finalizar")
def finalizar_campeonato(campeonato_id: int, db: Session = Depends(get_db)):
    """Finaliza un campeonato"""
    campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
    if not campeonato:
        raise HTTPException(status_code=404, detail="Campeonato no encontrado")
    
    campeonato.finalizado = True
    db.commit()
    db.refresh(campeonato)
    
    return {"message": "Campeonato finalizado correctamente"} 