from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_db
from app.models.mesa import Mesa
from app.models.resultado import Resultado
from app.models.pareja_partida import ParejaPartida
from app.schemas.mesa import MesaCreate, Mesa as MesaSchema
from app.schemas.pareja_partida import MesaSchema as MesaParejaSchema

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