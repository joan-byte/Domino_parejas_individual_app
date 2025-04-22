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
import logging

# Configurar logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/campeonatos",
    tags=["campeonatos"]
)

@router.get("/", response_model=List[CampeonatoResponse])
async def read_campeonatos(db: Session = Depends(get_db)):
    """Obtener lista de todos los campeonatos registrados en el sistema."""
    try:
        # Obtener los campeonatos de la base de datos
        campeonatos = db.query(Campeonato).all()
        logger.info(f"Campeonatos encontrados: {len(campeonatos)}")
        
        # Verificar si hay campeonatos
        if not campeonatos:
            logger.info("No se encontraron campeonatos en la base de datos")
            return []
            
        # Convertir los objetos SQLAlchemy a diccionarios
        campeonatos_response = []
        for campeonato in campeonatos:
            try:
                campeonato_dict = {
                    "id": campeonato.id,
                    "nombre": campeonato.nombre,
                    "fecha_inicio": campeonato.fecha_inicio,
                    "dias_duracion": campeonato.dias_duracion,
                    "numero_partidas": campeonato.numero_partidas,
                    "PM": campeonato.PM,
                    "activo": campeonato.activo,
                    "partida_actual": campeonato.partida_actual,
                    "finalizado": campeonato.finalizado
                }
                campeonatos_response.append(campeonato_dict)
            except Exception as e:
                logger.error(f"Error al procesar campeonato {campeonato.id}: {str(e)}")
                continue
        
        return campeonatos_response
        
    except Exception as e:
        logger.error(f"Error al obtener campeonatos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

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
    
    # Actualizar los campos permitidos por el schema CampeonatoUpdate
    update_data = campeonato.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_campeonato, key, value)
        
    # --- Lógica de Recálculo de 'finalizado' ---
    # Determinar si el campeonato debería estar finalizado AHORA.
    # Asumimos que está finalizado si partida_actual es >= numero_partidas.
    # (Asegúrate que la lógica de avance de partida_actual sea consistente con esto)
    if isinstance(db_campeonato.partida_actual, int) and isinstance(db_campeonato.numero_partidas, int):
         # Calcular el estado correcto basado en los números actuales
         should_be_finished = db_campeonato.partida_actual >= db_campeonato.numero_partidas
         
         # Si el estado calculado es diferente al estado actual en la BD, actualizarlo.
         if db_campeonato.finalizado != should_be_finished:
              db_campeonato.finalizado = should_be_finished
              logger.info(f"Campeonato ID {campeonato_id} 'finalizado' status recalculado y establecido a {should_be_finished} (partida_actual={db_campeonato.partida_actual}, numero_partidas={db_campeonato.numero_partidas}).")
    else:
         # Loguear una advertencia si los tipos no son correctos para la comparación
         logger.warning(f"No se pudo recalcular el estado 'finalizado' para Campeonato ID {campeonato_id} debido a tipos inválidos.")
    # -------------------------------------------
    
    logger.info(f"Antes de commit - ID: {db_campeonato.id}, finalizado: {db_campeonato.finalizado}")

    try:
        # Intentar guardar todos los cambios en la base de datos
        db.commit()
        logger.info(f"Después de commit - ¿Commit exitoso?")
    except Exception as e:
        # Si falla el commit, hacer rollback y loguear/lanzar error
        db.rollback()
        logger.error(f"Error durante db.commit() en campeonato {campeonato_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al guardar cambios en la base de datos")

    try:
        db.refresh(db_campeonato)
        logger.info(f"Después de refresh - ID: {db_campeonato.id}, finalizado: {db_campeonato.finalizado}")
    except Exception as e:
        logger.error(f"Error durante db.refresh() en campeonato {campeonato_id}: {str(e)}")
        # No relanzamos la excepción aquí, pero el estado puede ser inconsistente.
        # Devolver el objeto tal como estaba después del (potencialmente fallido) refresh.
        
    # Devolver el estado final del campeonato después del commit y refresh
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

@router.post("/{campeonato_id}/reactivar")
async def reactivar_campeonato(campeonato_id: int, db: Session = Depends(get_db)):
    """Reactivar un campeonato que está marcado como finalizado"""
    try:
        campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
        if not campeonato:
            raise HTTPException(status_code=404, detail="Campeonato no encontrado")
        
        campeonato.finalizado = False
        db.commit()
        
        return {"message": "Campeonato reactivado correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 