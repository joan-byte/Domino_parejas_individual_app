from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_db
from app.models.resultado import Resultado
from app.schemas.resultado import ResultadoMesaInput, Resultado as ResultadoSchema

router = APIRouter()

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
    resultados = db.query(Resultado).filter(
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