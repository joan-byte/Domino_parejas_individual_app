from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import random
from app.db.base import get_db
from app.models.pareja_partida import ParejaPartida
from app.models.resultado import Resultado
from app.schemas.pareja_partida import (
    ParejaPartidaCreate,
    ParejaPartida as ParejaPartidaSchema,
    SorteoInicial,
    AsignacionParejas,
    ParejaNueva
)
from app.models.jugador import Jugador
from app.models.campeonato import Campeonato

router = APIRouter(
    prefix="/parejas-partida",
    tags=["parejas-partida"]
)

@router.post("/sorteo-inicial/")
async def realizar_sorteo_inicial(sorteo: SorteoInicial, db: Session = Depends(get_db)):
    """Realiza el sorteo inicial de parejas y mesas para la primera partida"""
    try:
        # Verificar que todos los jugadores estén activos
        jugadores_activos = db.query(Jugador).filter(
            Jugador.id.in_(sorteo.jugadores),
            Jugador.activo == True
        ).all()
        
        jugadores_activos_ids = [j.id for j in jugadores_activos]
        jugadores_inactivos = set(sorteo.jugadores) - set(jugadores_activos_ids)
        
        if jugadores_inactivos:
            raise HTTPException(
                status_code=400, 
                detail=f"Los siguientes jugadores no están activos: {list(jugadores_inactivos)}"
            )
        
        # Verificar número par de jugadores
        if len(sorteo.jugadores) % 4 != 0:
            raise HTTPException(status_code=400, detail="El número de jugadores debe ser múltiplo de 4")
        
        # Mezclar aleatoriamente los jugadores
        jugadores = sorteo.jugadores.copy()
        random.shuffle(jugadores)
        
        # Crear las parejas y asignar mesas
        mesa = 1
        parejas = []
        
        # Procesar jugadores de 4 en 4 para formar las mesas
        for i in range(0, len(jugadores), 4):
            if i + 3 >= len(jugadores):
                break
            
            # Mezclar los 4 jugadores de esta mesa para formar parejas aleatorias
            mesa_jugadores = jugadores[i:i+4]
            random.shuffle(mesa_jugadores)
            
            # Crear primera pareja
            pareja1 = ParejaPartida(
                partida=1,
                mesa=mesa,
                jugador1_id=mesa_jugadores[0],
                jugador2_id=mesa_jugadores[1],
                numero_pareja=1,
                campeonato_id=sorteo.campeonato_id
            )
            
            # Crear segunda pareja
            pareja2 = ParejaPartida(
                partida=1,
                mesa=mesa,
                jugador1_id=mesa_jugadores[2],
                jugador2_id=mesa_jugadores[3],
                numero_pareja=2,
                campeonato_id=sorteo.campeonato_id
            )
            
            parejas.extend([pareja1, pareja2])
            mesa += 1
        
        # Guardar todas las parejas en la base de datos
        for pareja in parejas:
            db.add(pareja)
        
        db.commit()
        return {"message": "Sorteo inicial realizado con éxito"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parejas-partida/siguiente-partida/{campeonato_id}/{partida_actual}", response_model=List[ParejaPartidaSchema])
def crear_parejas_siguiente_partida(campeonato_id: int, partida_actual: int, db: Session = Depends(get_db)):
    """Crea las parejas para la siguiente partida basándose en el ranking"""
    
    # Calcular el ranking de jugadores
    ranking = db.query(
        Resultado.jugador_id,
        func.sum(Resultado.PG).label('total_PG'),
        func.sum(Resultado.PC).label('total_PC'),
        func.sum(Resultado.PT).label('total_PT')
    ).filter(
        Resultado.campeonato_id == campeonato_id,
        Resultado.partida <= partida_actual
    ).group_by(
        Resultado.jugador_id
    ).order_by(
        func.sum(Resultado.PG).desc(),
        func.sum(Resultado.PC).desc(),
        func.sum(Resultado.PT).desc()
    ).all()
    
    if not ranking:
        raise HTTPException(status_code=404, detail="No se encontraron resultados para calcular el ranking")
    
    # Obtener lista ordenada de jugadores por ranking
    jugadores_ordenados = [r[0] for r in ranking]  # Lista de IDs de jugadores ordenados por ranking
    
    parejas = []
    num_mesas = len(jugadores_ordenados) // 4
    siguiente_partida = partida_actual + 1
    
    # Crear parejas según el ranking
    for mesa in range(1, num_mesas + 1):
        idx_base = (mesa - 1) * 4
        
        # Pareja 1: jugador ranking 4n+1 con jugador ranking 4n+3
        pareja1 = ParejaPartida(
            partida=siguiente_partida,
            mesa=mesa,
            jugador1_id=jugadores_ordenados[idx_base],      # Posición 4n+1
            jugador2_id=jugadores_ordenados[idx_base + 2],  # Posición 4n+3
            numero_pareja=1,
            campeonato_id=campeonato_id
        )
        
        # Pareja 2: jugador ranking 4n+2 con jugador ranking 4n+4
        pareja2 = ParejaPartida(
            partida=siguiente_partida,
            mesa=mesa,
            jugador1_id=jugadores_ordenados[idx_base + 1],  # Posición 4n+2
            jugador2_id=jugadores_ordenados[idx_base + 3],  # Posición 4n+4
            numero_pareja=2,
            campeonato_id=campeonato_id
        )
        
        db.add(pareja1)
        db.add(pareja2)
        parejas.extend([pareja1, pareja2])
    
    db.commit()
    for pareja in parejas:
        db.refresh(pareja)
    
    return parejas

@router.get("/campeonato/{campeonato_id}/partida/{partida}", response_model=List[ParejaPartidaSchema])
def get_parejas_partida(campeonato_id: int, partida: int, db: Session = Depends(get_db)):
    """Obtiene todas las parejas de una partida específica"""
    try:
        parejas = db.query(ParejaPartida).filter(
            ParejaPartida.campeonato_id == campeonato_id,
            ParejaPartida.partida == partida
        ).all()

        # Cargar los datos de los jugadores para cada pareja
        for pareja in parejas:
            # Cargar jugador1
            pareja.jugador1 = db.query(Jugador).filter(Jugador.id == pareja.jugador1_id).first()
            # Cargar jugador2
            pareja.jugador2 = db.query(Jugador).filter(Jugador.id == pareja.jugador2_id).first()

        return parejas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/parejas-partida/mesa/{campeonato_id}/{partida}/{mesa}", response_model=List[ParejaPartidaSchema])
def get_parejas_mesa(campeonato_id: int, partida: int, mesa: int, db: Session = Depends(get_db)):
    """Obtiene las parejas de una mesa específica"""
    parejas = db.query(ParejaPartida).filter(
        ParejaPartida.campeonato_id == campeonato_id,
        ParejaPartida.partida == partida,
        ParejaPartida.mesa == mesa
    ).order_by(ParejaPartida.numero_pareja).all()
    return parejas

@router.delete("/parejas-partida/eliminar/{campeonato_id}/{partida}")
def eliminar_parejas_partida(campeonato_id: int, partida: int, db: Session = Depends(get_db)):
    """Elimina todas las parejas de una partida específica"""
    parejas = db.query(ParejaPartida).filter(
        ParejaPartida.campeonato_id == campeonato_id,
        ParejaPartida.partida == partida
    ).all()
    
    if not parejas:
        raise HTTPException(status_code=404, detail="No se encontraron parejas para eliminar")
    
    for pareja in parejas:
        db.delete(pareja)
    
    db.commit()
    return {"message": "Parejas eliminadas correctamente"}

@router.post("/parejas-partida/asignar", response_model=List[ParejaPartidaSchema])
def asignar_parejas(datos: AsignacionParejas, db: Session = Depends(get_db)):
    """Asigna las parejas para una partida"""
    try:
        nuevas_parejas = []
        # Agrupar parejas por mesa
        parejas_por_mesa = {}
        for pareja in datos.parejas:
            if pareja.mesa not in parejas_por_mesa:
                parejas_por_mesa[pareja.mesa] = []
            parejas_por_mesa[pareja.mesa].append(pareja)
        
        # Crear las parejas asignando el número correcto
        for mesa, parejas in parejas_por_mesa.items():
            for i, pareja in enumerate(parejas, 1):
                nueva_pareja = ParejaPartida(
                    partida=pareja.partida,
                    mesa=pareja.mesa,
                    jugador1_id=pareja.jugador1_id,
                    jugador2_id=pareja.jugador2_id,
                    numero_pareja=i,  # 1 para la primera pareja, 2 para la segunda
                    campeonato_id=datos.campeonato_id
                )
                db.add(nueva_pareja)
                nuevas_parejas.append(nueva_pareja)
        
        db.commit()
        for pareja in nuevas_parejas:
            db.refresh(pareja)
        
        return nuevas_parejas
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al asignar parejas: {str(e)}")

@router.get("/ultima-partida/{campeonato_id}")
def get_ultima_partida(campeonato_id: int, db: Session = Depends(get_db)):
    """Obtiene el número de la última partida registrada para un campeonato"""
    try:
        # Primero verificar si existen registros para este campeonato
        existe_registro = db.query(ParejaPartida).filter(
            ParejaPartida.campeonato_id == campeonato_id
        ).first()
        
        if not existe_registro:
            return {"ultima_partida": 0, "tiene_registros": False}
            
        ultima_partida = db.query(func.max(ParejaPartida.partida)).filter(
            ParejaPartida.campeonato_id == campeonato_id
        ).scalar()
        
        return {
            "ultima_partida": ultima_partida if ultima_partida is not None else 0,
            "tiene_registros": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/partidas/cerrar/{campeonato_id}/{partida}")
async def cerrar_partida(campeonato_id: int, partida: int, db: Session = Depends(get_db)):
    """Cierra una partida y actualiza la partida actual del campeonato"""
    # Verificar que el campeonato existe
    campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
    if not campeonato:
        raise HTTPException(status_code=404, detail="Campeonato no encontrado")
    
    # Verificar que la partida actual coincide
    if campeonato.partida_actual != partida:
        raise HTTPException(status_code=400, detail="La partida no coincide con la partida actual del campeonato")
    
    # Actualizar la partida actual del campeonato
    nueva_partida = partida + 1
    if nueva_partida <= campeonato.numero_partidas:
        campeonato.partida_actual = nueva_partida
    else:
        campeonato.finalizado = True
    
    try:
        db.commit()
        return {"message": "Partida cerrada exitosamente", "nueva_partida": nueva_partida}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 