from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.db.base import get_db
from app.models.resultado import Resultado
from app.models.jugador import Jugador
from app.schemas.resultado import ResultadoMesaInput, Resultado as ResultadoSchema
from sqlalchemy.sql import func

router = APIRouter(
    prefix="/api/v1",
    tags=["resultados"]
)

def calcular_PV(PT: int) -> int:
    """Calcula los Puntos Válidos (máximo 300)"""
    return min(PT, 300)

@router.post("/resultados/mesa/", response_model=List[ResultadoSchema])
def create_resultados_mesa(datos: ResultadoMesaInput, db: Session = Depends(get_db)):
    # Calcular PV para cada pareja
    PV_pareja1 = calcular_PV(datos.puntos_pareja1)
    PV_pareja2 = calcular_PV(datos.puntos_pareja2)
    
    # Calcular PC para cada pareja
    PC_pareja1 = PV_pareja1 - PV_pareja2
    PC_pareja2 = PV_pareja2 - PV_pareja1
    
    # Calcular PG para cada pareja
    PG_pareja1 = 1 if PC_pareja1 > 0 else 0
    PG_pareja2 = 1 if PC_pareja2 > 0 else 0
    
    # Crear los 4 registros (uno por cada jugador)
    resultados = []
    
    # Jugadores de la pareja 1
    for num_jugador, jugador_id in [(1, datos.jugador1_id), (2, datos.jugador2_id)]:
        resultado = Resultado(
            partida=datos.partida,
            mesa=datos.mesa,
            jugador=num_jugador,
            jugador_id=jugador_id,
            PT=datos.puntos_pareja1,  # Puntos totales de su pareja
            PV=PV_pareja1,           # Puntos válidos de su pareja
            PC=PC_pareja1,           # Puntos conseguidos por su pareja
            PG=PG_pareja1,           # Si su pareja ganó
            campeonato_id=datos.campeonato_id
        )
        db.add(resultado)
        resultados.append(resultado)
    
    # Jugadores de la pareja 2
    for num_jugador, jugador_id in [(3, datos.jugador3_id), (4, datos.jugador4_id)]:
        resultado = Resultado(
            partida=datos.partida,
            mesa=datos.mesa,
            jugador=num_jugador,
            jugador_id=jugador_id,
            PT=datos.puntos_pareja2,  # Puntos totales de su pareja
            PV=PV_pareja2,           # Puntos válidos de su pareja
            PC=PC_pareja2,           # Puntos conseguidos por su pareja
            PG=PG_pareja2,           # Si su pareja ganó
            campeonato_id=datos.campeonato_id
        )
        db.add(resultado)
        resultados.append(resultado)
    
    db.commit()
    for resultado in resultados:
        db.refresh(resultado)
    
    return resultados

@router.get("/resultados/", response_model=List[ResultadoSchema])
def read_resultados(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    resultados = db.query(Resultado).offset(skip).limit(limit).all()
    return resultados

@router.get("/resultados/campeonato/{campeonato_id}/partida/{partida}", response_model=List[ResultadoSchema])
def read_resultados_by_campeonato_partida(campeonato_id: int, partida: int, db: Session = Depends(get_db)):
    """Obtiene todos los resultados de una partida en un campeonato"""
    resultados = db.query(Resultado).join(
        Jugador, Resultado.jugador_id == Jugador.id
    ).filter(
        Resultado.campeonato_id == campeonato_id,
        Resultado.partida == partida
    ).order_by(Resultado.mesa, Resultado.jugador).all()
    
    return resultados

@router.get("/resultados/jugador/{jugador_id}/campeonato/{campeonato_id}", response_model=List[ResultadoSchema])
def read_resultados_by_jugador_campeonato(jugador_id: int, campeonato_id: int, db: Session = Depends(get_db)):
    """Obtiene todos los resultados de un jugador en un campeonato"""
    resultados = db.query(Resultado).filter(
        Resultado.jugador_id == jugador_id,
        Resultado.campeonato_id == campeonato_id
    ).order_by(Resultado.partida, Resultado.mesa).all()
    return resultados

@router.get("/resultados/mesa/{campeonato_id}/{partida}/{mesa}", response_model=List[ResultadoSchema])
def read_resultados_by_mesa(campeonato_id: int, partida: int, mesa: int, db: Session = Depends(get_db)):
    """Obtiene los 4 resultados de una mesa específica"""
    resultados = db.query(Resultado).filter(
        Resultado.campeonato_id == campeonato_id,
        Resultado.partida == partida,
        Resultado.mesa == mesa
    ).order_by(Resultado.jugador).all()
    return resultados

@router.put("/resultados/mesa/", response_model=List[ResultadoSchema])
def update_resultados_mesa(datos: ResultadoMesaInput, db: Session = Depends(get_db)):
    """Actualiza los resultados existentes de una mesa"""
    # Primero verificamos que existan los resultados
    resultados = db.query(Resultado).filter(
        Resultado.campeonato_id == datos.campeonato_id,
        Resultado.partida == datos.partida,
        Resultado.mesa == datos.mesa
    ).all()
    
    if not resultados:
        raise HTTPException(status_code=404, detail="No se encontraron resultados para actualizar")
    
    # Calcular los nuevos valores
    PV_pareja1 = calcular_PV(datos.puntos_pareja1)
    PV_pareja2 = calcular_PV(datos.puntos_pareja2)
    
    PC_pareja1 = PV_pareja1 - PV_pareja2
    PC_pareja2 = PV_pareja2 - PV_pareja1
    
    PG_pareja1 = 1 if PC_pareja1 > 0 else 0
    PG_pareja2 = 1 if PC_pareja2 > 0 else 0
    
    # Actualizar los resultados existentes
    for resultado in resultados:
        if resultado.jugador in [1, 2]:  # Pareja 1
            resultado.PT = datos.puntos_pareja1
            resultado.PV = PV_pareja1
            resultado.PC = PC_pareja1
            resultado.PG = PG_pareja1
        else:  # Pareja 2
            resultado.PT = datos.puntos_pareja2
            resultado.PV = PV_pareja2
            resultado.PC = PC_pareja2
            resultado.PG = PG_pareja2
    
    db.commit()
    for resultado in resultados:
        db.refresh(resultado)
    
    return resultados

@router.get("/ranking/campeonato/{campeonato_id}")
async def get_ranking_campeonato(campeonato_id: int, db: Session = Depends(get_db)):
    """Obtiene el ranking de jugadores de un campeonato"""
    
    # Obtener todos los resultados del campeonato
    ranking = db.query(
        Resultado.jugador_id,
        Jugador.nombre,
        Jugador.apellidos,
        Jugador.club,
        func.sum(Resultado.PT).label('PT'),
        func.sum(Resultado.PG).label('PG'),
        func.sum(Resultado.PC).label('PC'),
        func.max(Resultado.partida).label('ultima_partida')
    ).join(
        Jugador, Resultado.jugador_id == Jugador.id
    ).filter(
        Resultado.campeonato_id == campeonato_id
    ).group_by(
        Resultado.jugador_id,
        Jugador.nombre,
        Jugador.apellidos,
        Jugador.club
    ).order_by(
        func.sum(Resultado.PG).desc(),
        func.sum(Resultado.PC).desc(),
        func.sum(Resultado.PT).desc()
    ).all()
    
    if not ranking:
        raise HTTPException(status_code=404, detail="No se encontraron resultados para este campeonato")
    
    # Convertir los resultados a un formato más amigable
    ranking_list = []
    for r in ranking:
        ranking_list.append({
            "jugador_id": r.jugador_id,
            "nombre": r.nombre,
            "apellidos": r.apellidos,
            "club": r.club,
            "PT": int(r.PT),
            "PG": int(r.PG),
            "PC": int(r.PC),
            "ultima_partida": int(r.ultima_partida)
        })
    
    return ranking_list

@router.get("/resultados/campeonato/{campeonato_id}/hasta-partida/{partida}", response_model=List[ResultadoSchema])
def read_resultados_hasta_partida(campeonato_id: int, partida: int, db: Session = Depends(get_db)):
    """Obtiene todos los resultados de un campeonato hasta una partida específica"""
    resultados = db.query(Resultado).filter(
        Resultado.campeonato_id == campeonato_id,
        Resultado.partida <= partida
    ).order_by(Resultado.partida, Resultado.mesa, Resultado.jugador).all()
    return resultados 