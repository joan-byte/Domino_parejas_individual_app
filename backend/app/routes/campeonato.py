from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging
from app.db.base import get_db
from app.models.campeonato import Campeonato
from app.schemas.campeonato import CampeonatoCreate, CampeonatoResponse, CampeonatoUpdate

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Crear el router con configuración explícita
router = APIRouter(
    prefix="/api/v1/campeonatos",
    tags=["campeonatos"]
)

@router.get("/", response_model=List[CampeonatoResponse])
async def read_campeonatos(db: Session = Depends(get_db)):
    """
    Obtener lista de todos los campeonatos registrados en el sistema.
    """
    logger.debug("GET /api/v1/campeonatos/ llamado")
    try:
        logger.debug("Intentando consultar campeonatos en la base de datos...")
        campeonatos = db.query(Campeonato).all()
        logger.info(f"Campeonatos encontrados: {len(campeonatos)}")
        if len(campeonatos) == 0:
            logger.warning("No se encontraron campeonatos en la base de datos")
        else:
            logger.debug(f"IDs de campeonatos encontrados: {[c.id for c in campeonatos]}")
        return campeonatos
    except Exception as e:
        logger.error(f"Error al obtener campeonatos: {str(e)}")
        logger.exception("Detalles del error:")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=CampeonatoResponse, status_code=201)
async def create_campeonato(campeonato: CampeonatoCreate, db: Session = Depends(get_db)):
    logger.debug("POST /api/v1/campeonatos llamado")
    try:
        db_campeonato = Campeonato(**campeonato.dict())
        db.add(db_campeonato)
        db.commit()
        db.refresh(db_campeonato)
        logger.info(f"Campeonato creado con ID: {db_campeonato.id}")
        return db_campeonato
    except Exception as e:
        logger.error(f"Error al crear campeonato: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{campeonato_id}", response_model=CampeonatoResponse)
async def read_campeonato(campeonato_id: int, db: Session = Depends(get_db)):
    logger.debug(f"GET /campeonatos/{campeonato_id} llamado")
    campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
    if campeonato is None:
        logger.warning(f"Campeonato con ID {campeonato_id} no encontrado")
        raise HTTPException(status_code=404, detail="Campeonato no encontrado")
    logger.info(f"Campeonato encontrado: {campeonato.id}")
    return campeonato

@router.put("/{campeonato_id}", response_model=CampeonatoResponse)
async def update_campeonato(campeonato_id: int, campeonato: CampeonatoUpdate, db: Session = Depends(get_db)):
    logger.debug(f"PUT /campeonatos/{campeonato_id} llamado")
    db_campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
    if db_campeonato is None:
        logger.warning(f"Campeonato con ID {campeonato_id} no encontrado")
        raise HTTPException(status_code=404, detail="Campeonato no encontrado")
    
    for key, value in campeonato.dict(exclude_unset=True).items():
        setattr(db_campeonato, key, value)
    
    db.commit()
    db.refresh(db_campeonato)
    logger.info(f"Campeonato {campeonato_id} actualizado")
    return db_campeonato

@router.delete("/{campeonato_id}", status_code=204)
async def delete_campeonato(campeonato_id: int, db: Session = Depends(get_db)):
    logger.debug(f"DELETE /campeonatos/{campeonato_id} llamado")
    db_campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
    if db_campeonato is None:
        logger.warning(f"Campeonato con ID {campeonato_id} no encontrado")
        raise HTTPException(status_code=404, detail="Campeonato no encontrado")
    
    db.delete(db_campeonato)
    db.commit()
    logger.info(f"Campeonato {campeonato_id} eliminado")
    return {"message": "Campeonato eliminado"} 