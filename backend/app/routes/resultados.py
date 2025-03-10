from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.models import Campeonato, Mesa, Resultado
from backend.database.database import get_db

router = APIRouter()

@router.get("/mesas-registradas/{campeonato_id}/{partida}")
def get_mesas_registradas(campeonato_id: int, partida: int, db: Session = Depends(get_db)):
    """Obtiene las mesas que tienen resultados registrados para una partida específica"""
    # Verificar que el campeonato existe
    campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
    if not campeonato:
        raise HTTPException(status_code=404, detail="Campeonato no encontrado")
    
    # Obtener todas las mesas para esta partida
    mesas = db.query(Mesa).filter(
        Mesa.campeonato_id == campeonato_id,
        Mesa.partida == partida
    ).all()
    
    # Obtener los resultados registrados
    resultados = db.query(Resultado).filter(
        Resultado.campeonato_id == campeonato_id,
        Resultado.partida == partida
    ).all()
    
    # Crear un diccionario con las mesas que tienen resultados
    mesas_registradas = {}
    for resultado in resultados:
        mesas_registradas[resultado.mesa] = True
    
    # Verificar si todas las mesas tienen resultados
    todas_registradas = True
    if mesas:
        for mesa in mesas:
            if mesa.numero not in mesas_registradas:
                todas_registradas = False
                break
    else:
        todas_registradas = False
    
    return {
        "mesas_registradas": mesas_registradas,
        "todas_registradas": todas_registradas
    } 