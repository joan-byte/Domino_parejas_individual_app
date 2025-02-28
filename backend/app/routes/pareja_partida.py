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
    ParejaNueva,
    SiguientePartidaResponse
)
from app.models.jugador import Jugador
from app.models.campeonato import Campeonato

router = APIRouter(
    prefix="/parejas-partida",
    tags=["parejas-partida"]
)

@router.post("/sorteo-inicial/")
async def realizar_sorteo_inicial(sorteo: SorteoInicial, db: Session = Depends(get_db)):
    """Realiza el sorteo inicial de parejas y mesas para la primera partida.
    Los jugadores que no puedan formar una mesa completa quedarán sin asignar."""
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
        
        # Mezclar aleatoriamente los jugadores
        jugadores = sorteo.jugadores.copy()
        random.shuffle(jugadores)
        
        # Crear las parejas y asignar mesas
        mesa = 1
        parejas = []
        jugadores_sin_asignar = []
        
        # Procesar jugadores de 4 en 4 para formar las mesas completas
        for i in range(0, len(jugadores) - 3, 4):  # Modificado para evitar índices fuera de rango
            # Mezclar los 4 jugadores de esta mesa para formar parejas aleatorias
            mesa_jugadores = jugadores[i:i+4]
            if len(mesa_jugadores) < 4:  # Si no hay suficientes jugadores para una mesa completa
                jugadores_sin_asignar.extend(mesa_jugadores)
                break
                
            random.shuffle(mesa_jugadores)
            
            # Crear primera pareja
            pareja1 = ParejaPartida(
                partida=1,  # Primera partida real
                mesa=mesa,
                jugador1_id=mesa_jugadores[0],
                jugador2_id=mesa_jugadores[1],
                numero_pareja=1,
                campeonato_id=sorteo.campeonato_id
            )
            
            # Crear segunda pareja
            pareja2 = ParejaPartida(
                partida=1,  # Primera partida real
                mesa=mesa,
                jugador1_id=mesa_jugadores[2],
                jugador2_id=mesa_jugadores[3],
                numero_pareja=2,
                campeonato_id=sorteo.campeonato_id
            )
            
            parejas.extend([pareja1, pareja2])
            mesa += 1
        
        # Agregar los últimos jugadores a la lista de sin asignar si no completan una mesa
        if len(jugadores) % 4 != 0:
            ultimo_indice = (len(jugadores) // 4) * 4
            jugadores_sin_asignar.extend(jugadores[ultimo_indice:])
        
        # Actualizar el campeonato a partida 1
        campeonato = db.query(Campeonato).filter(Campeonato.id == sorteo.campeonato_id).first()
        if not campeonato:
            raise HTTPException(status_code=404, detail="Campeonato no encontrado")
        campeonato.partida_actual = 1  # Actualizar a primera partida real
        
        # Guardar todas las parejas en la base de datos
        for pareja in parejas:
            db.add(pareja)
        
        db.commit()
        return {
            "message": "Sorteo inicial realizado con éxito",
            "jugadores_sin_asignar": jugadores_sin_asignar,
            "mesas_formadas": mesa - 1
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/siguiente-partida/{campeonato_id}/{partida_actual}", response_model=SiguientePartidaResponse)
def crear_parejas_siguiente_partida(campeonato_id: int, partida_actual: int, db: Session = Depends(get_db)):
    """Crea las parejas para la siguiente partida basándose en el ranking.
    Solo se consideran jugadores activos para la asignación.
    La última mesa puede tener de 1 a 4 jugadores.
    
    La asignación sigue el siguiente patrón:
    Mesa 1: Pareja 1 (1º y 3º) vs Pareja 2 (2º y 4º)
    Mesa 2: Pareja 1 (5º y 7º) vs Pareja 2 (6º y 8º)
    Mesa 3: Pareja 1 (9º y 11º) vs Pareja 2 (10º y 12º)
    Y así sucesivamente...
    """
    try:
        # Obtener la última partida asignada en la base de datos
        ultima_partida = db.query(func.max(ParejaPartida.partida)).filter(
            ParejaPartida.campeonato_id == campeonato_id
        ).scalar()
        
        # Si no hay partidas previas, comenzar desde la partida 1
        if ultima_partida is None:
            siguiente_partida = 1
        else:
            siguiente_partida = ultima_partida + 1

        # Verificar que el campeonato existe y actualizar su partida actual
        campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
        if not campeonato:
            raise HTTPException(status_code=404, detail="Campeonato no encontrado")
            
        campeonato.partida_actual = siguiente_partida
        
        # Obtener solo jugadores activos
        jugadores_activos = db.query(Jugador.id).filter(
            Jugador.campeonato_id == campeonato_id,
            Jugador.activo == True
        ).all()
        
        if not jugadores_activos:
            raise HTTPException(status_code=400, detail="No hay jugadores activos disponibles")
            
        jugadores_activos_ids = [j[0] for j in jugadores_activos]
        
        # Obtener el ranking actual usando los criterios correctos, solo para jugadores activos
        ranking = db.query(
            Resultado.jugador_id,
            func.sum(Resultado.PG).label('total_PG'),
            func.sum(Resultado.PC).label('total_PC'),
            func.sum(Resultado.PT).label('total_PT'),
            func.sum(Resultado.MG).label('total_MG')
        ).filter(
            Resultado.campeonato_id == campeonato_id,
            Resultado.partida < siguiente_partida,
            Resultado.jugador_id.in_(jugadores_activos_ids)
        ).group_by(
            Resultado.jugador_id
        ).order_by(
            func.sum(Resultado.PG).desc(),
            func.sum(Resultado.PC).desc(),
            func.sum(Resultado.PT).desc(),
            func.sum(Resultado.MG),
            Resultado.jugador_id.asc()
        ).all()

        # Si no hay ranking (primera partida), obtener jugadores en orden aleatorio
        if not ranking:
            jugadores_ordenados = [j[0] for j in jugadores_activos]
            random.shuffle(jugadores_ordenados)
        else:
            jugadores_ordenados = [r[0] for r in ranking]

        parejas = []
        num_jugadores = len(jugadores_ordenados)
        
        # Calcular el número de mesas completas y jugadores restantes
        num_mesas_completas = num_jugadores // 4
        jugadores_restantes = num_jugadores % 4
        
        # Crear parejas para las mesas completas
        for mesa in range(num_mesas_completas):
            indice_base = mesa * 4
            
            # Pareja 1: jugadores en posiciones base y base+2
            pareja1 = ParejaPartida(
                partida=siguiente_partida,
                mesa=mesa + 1,
                jugador1_id=jugadores_ordenados[indice_base],
                jugador2_id=jugadores_ordenados[indice_base + 2],
                numero_pareja=1,
                campeonato_id=campeonato_id
            )
            
            # Pareja 2: jugadores en posiciones base+1 y base+3
            pareja2 = ParejaPartida(
                partida=siguiente_partida,
                mesa=mesa + 1,
                jugador1_id=jugadores_ordenados[indice_base + 1],
                jugador2_id=jugadores_ordenados[indice_base + 3],
                numero_pareja=2,
                campeonato_id=campeonato_id
            )
            
            db.add(pareja1)
            db.add(pareja2)
            parejas.extend([pareja1, pareja2])

        # Manejar los jugadores restantes en la última mesa
        if jugadores_restantes > 0:
            ultima_mesa = num_mesas_completas + 1
            indice_inicio = num_mesas_completas * 4
            
            # Si hay jugadores restantes, crear al menos una pareja
            if jugadores_restantes >= 1:
                # Si hay al menos 2 jugadores, crear una pareja completa
                if jugadores_restantes >= 2:
                    pareja_ultima = ParejaPartida(
                        partida=siguiente_partida,
                        mesa=ultima_mesa,
                        jugador1_id=jugadores_ordenados[indice_inicio],
                        jugador2_id=jugadores_ordenados[indice_inicio + 1],
                        numero_pareja=1,
                        campeonato_id=campeonato_id
                    )
                    db.add(pareja_ultima)
                    parejas.append(pareja_ultima)
                    
                    # Si hay 3 o 4 jugadores, crear la segunda pareja
                    if jugadores_restantes >= 3:
                        # Para 3 jugadores, crear una pareja con un solo jugador
                        if jugadores_restantes == 3:
                            pareja_ultima2 = ParejaPartida(
                                partida=siguiente_partida,
                                mesa=ultima_mesa,
                                jugador1_id=jugadores_ordenados[indice_inicio + 2],
                                jugador2_id=None,  # Pareja incompleta
                                numero_pareja=2,
                                campeonato_id=campeonato_id
                            )
                        # Para 4 jugadores, crear una pareja completa
                        else:
                            pareja_ultima2 = ParejaPartida(
                                partida=siguiente_partida,
                                mesa=ultima_mesa,
                                jugador1_id=jugadores_ordenados[indice_inicio + 2],
                                jugador2_id=jugadores_ordenados[indice_inicio + 3],
                                numero_pareja=2,
                                campeonato_id=campeonato_id
                            )
                        db.add(pareja_ultima2)
                        parejas.append(pareja_ultima2)
                # Si solo hay 1 jugador, crear una pareja incompleta
                else:
                    pareja_ultima = ParejaPartida(
                        partida=siguiente_partida,
                        mesa=ultima_mesa,
                        jugador1_id=jugadores_ordenados[indice_inicio],
                        jugador2_id=None,  # Pareja incompleta
                        numero_pareja=1,
                        campeonato_id=campeonato_id
                    )
                    db.add(pareja_ultima)
                    parejas.append(pareja_ultima)

        db.commit()

        # Calcular el número total de mesas formadas
        total_mesas = num_mesas_completas + (1 if jugadores_restantes > 0 else 0)
        
        # No hay jugadores sin asignar ya que todos se asignan a mesas
        jugadores_sin_asignar = []
        
        return SiguientePartidaResponse(
            parejas=parejas,
            jugadores_sin_asignar=jugadores_sin_asignar,
            mesas_formadas=total_mesas
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

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

@router.delete("/eliminar/{campeonato_id}/{partida}")
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
    """Asigna las parejas para una partida.
    Solo permite asignar jugadores que estén activos."""
    try:
        # Obtener jugadores activos
        jugadores_activos = db.query(Jugador.id).filter(
            Jugador.campeonato_id == datos.campeonato_id,
            Jugador.activo == True
        ).all()
        
        jugadores_activos_ids = {j[0] for j in jugadores_activos}
        
        # Verificar que todos los jugadores en las parejas estén activos
        for pareja in datos.parejas:
            if pareja.jugador1_id not in jugadores_activos_ids or pareja.jugador2_id not in jugadores_activos_ids:
                raise HTTPException(
                    status_code=400,
                    detail="Solo se pueden asignar jugadores activos"
                )
        
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
        # Verificar si el campeonato existe
        campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
        if not campeonato:
            raise HTTPException(status_code=404, detail="Campeonato no encontrado")

        # Verificar si existen registros para este campeonato
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
        print(f"Error al obtener última partida: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener última partida: {str(e)}")

@router.post("/partidas/cerrar/{campeonato_id}/{partida}")
async def cerrar_partida(campeonato_id: int, partida: int, db: Session = Depends(get_db)):
    """Cierra una partida y actualiza la partida actual del campeonato."""
    try:
        # Verificar que el campeonato existe
        campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
        if not campeonato:
            raise HTTPException(status_code=404, detail="Campeonato no encontrado")

        # Verificar que existen parejas para esta partida
        parejas = db.query(ParejaPartida).filter(
            ParejaPartida.campeonato_id == campeonato_id,
            ParejaPartida.partida == partida
        ).all()
        
        if not parejas:
            raise HTTPException(
                status_code=400,
                detail=f"No se encontraron parejas para la partida {partida}"
            )

        # Obtener todos los jugadores que participaron en esta partida
        jugadores_participantes = set()
        for pareja in parejas:
            if pareja.jugador1_id:  # Agregar jugador1 si existe
                jugadores_participantes.add(pareja.jugador1_id)
            if pareja.jugador2_id:  # Agregar jugador2 solo si existe
                jugadores_participantes.add(pareja.jugador2_id)

        # Verificar si hay resultados para todos los jugadores de esta partida
        resultados = db.query(Resultado).filter(
            Resultado.campeonato_id == campeonato_id,
            Resultado.partida == partida,
            Resultado.jugador_id.in_(list(jugadores_participantes))
        ).all()
        
        jugadores_con_resultado = {r.jugador_id for r in resultados}
        jugadores_sin_resultado = jugadores_participantes - jugadores_con_resultado
        
        if jugadores_sin_resultado:
            raise HTTPException(
                status_code=400, 
                detail=f"Faltan resultados para los siguientes jugadores: {list(jugadores_sin_resultado)}"
            )
        
        # Obtener la última partida registrada
        ultima_partida = db.query(func.max(ParejaPartida.partida)).filter(
            ParejaPartida.campeonato_id == campeonato_id
        ).scalar() or 0

        # Actualizar la partida actual del campeonato
        nueva_partida = max(partida + 1, ultima_partida + 1)
        campeonato.partida_actual = nueva_partida
            
        # Verificar si esta es la última partida
        if campeonato.partida_actual > campeonato.numero_partidas:
            campeonato.finalizado = True
        
        db.commit()
        return {
            "message": "Partida cerrada exitosamente",
            "nueva_partida": campeonato.partida_actual,
            "campeonato_finalizado": campeonato.finalizado
        }
            
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        print(f"Error al cerrar partida: {str(e)}")  # Añadir log del error
        raise HTTPException(
            status_code=500,
            detail=f"Error al cerrar la partida: {str(e)}"
        )

@router.post("/corregir-asignacion/{campeonato_id}/{partida}", response_model=List[ParejaPartidaSchema])
def corregir_asignacion_parejas(campeonato_id: int, partida: int, db: Session = Depends(get_db)):
    """Corrige la asignación de parejas de una partida específica según el ranking.
    
    La asignación sigue el siguiente patrón:
    Mesa 1: Pareja 1 (1º y 3º) vs Pareja 2 (2º y 4º)
    Mesa 2: Pareja 1 (5º y 7º) vs Pareja 2 (6º y 8º)
    Mesa 3: Pareja 1 (9º y 11º) vs Pareja 2 (10º y 12º)
    Y así sucesivamente...
    
    El orden de clasificación es:
    1. Suma de PG (Partidas Ganadas) descendente
    2. Suma de PC (Puntos Conseguidos) descendente
    3. Suma de PT (Puntos Totales) descendente
    4. Suma de MG (Manos Ganadas) ascendente
    """
    # Verificar si hay resultados registrados para esta partida
    resultados_existentes = db.query(Resultado).filter(
        Resultado.campeonato_id == campeonato_id,
        Resultado.partida == partida
    ).first()
    
    if resultados_existentes:
        raise HTTPException(
            status_code=400, 
            detail="No se puede corregir la asignación porque ya hay resultados registrados para esta partida"
        )
    
    # Calcular el ranking hasta la partida anterior usando los criterios correctos
    ranking_query = db.query(
        Resultado.jugador_id,
        func.sum(Resultado.PG).label('total_PG'),
        func.sum(Resultado.PC).label('total_PC'),
        func.sum(Resultado.PT).label('total_PT'),
        func.sum(Resultado.MG).label('total_MG')
    ).filter(
        Resultado.campeonato_id == campeonato_id,
        Resultado.partida < partida  # Solo considerar partidas anteriores
    ).group_by(
        Resultado.jugador_id
    ).order_by(
        func.sum(Resultado.PG).desc(),  # 1º criterio: PG descendente
        func.sum(Resultado.PC).desc(),  # 2º criterio: PC descendente
        func.sum(Resultado.PT).desc(),  # 3º criterio: PT descendente
        func.sum(Resultado.MG),         # 4º criterio: MG ascendente
        Resultado.jugador_id.asc()      # 5º criterio: ID del jugador ascendente para desempate
    )
    
    # Obtener los resultados completos para poder verificar empates
    ranking_results = ranking_query.all()
    
    # Si es la primera partida y no hay ranking, usar el orden del sorteo inicial
    if not ranking_results and partida == 1:
        jugadores_ordenados = db.query(
            ParejaPartida.jugador1_id
        ).filter(
            ParejaPartida.campeonato_id == campeonato_id,
            ParejaPartida.partida == 1
        ).order_by(
            ParejaPartida.mesa,
            ParejaPartida.numero_pareja
        ).all()
        jugadores_ordenados.extend(db.query(
            ParejaPartida.jugador2_id
        ).filter(
            ParejaPartida.campeonato_id == campeonato_id,
            ParejaPartida.partida == 1
        ).order_by(
            ParejaPartida.mesa,
            ParejaPartida.numero_pareja
        ).all())
        jugadores_ordenados = [j[0] for j in jugadores_ordenados]
    else:
        # Extraer los IDs de los jugadores en el orden correcto
        jugadores_ordenados = [r[0] for r in ranking_results]
    
    if not jugadores_ordenados:
        raise HTTPException(status_code=404, detail="No se encontraron jugadores para realizar la asignación")
    
    # Eliminar las parejas existentes de esta partida
    db.query(ParejaPartida).filter(
        ParejaPartida.campeonato_id == campeonato_id,
        ParejaPartida.partida == partida
    ).delete()
    
    parejas = []
    num_mesas = len(jugadores_ordenados) // 4
    
    # Crear todas las parejas
    for mesa in range(num_mesas):
        indice_base = mesa * 4  # Índice base para esta mesa
        
        # Pareja 1: jugadores en posiciones base y base+2 (1º y 3º, 5º y 7º, etc.)
        pareja1 = ParejaPartida(
            partida=partida,
            mesa=mesa + 1,
            jugador1_id=jugadores_ordenados[indice_base],     # 1º, 5º, 9º...
            jugador2_id=jugadores_ordenados[indice_base + 2], # 3º, 7º, 11º...
            numero_pareja=1,
            campeonato_id=campeonato_id
        )
        
        # Pareja 2: jugadores en posiciones base+1 y base+3 (2º y 4º, 6º y 8º, etc.)
        pareja2 = ParejaPartida(
            partida=partida,
            mesa=mesa + 1,
            jugador1_id=jugadores_ordenados[indice_base + 1], # 2º, 6º, 10º...
            jugador2_id=jugadores_ordenados[indice_base + 3], # 4º, 8º, 12º...
            numero_pareja=2,
            campeonato_id=campeonato_id
        )
        
        db.add(pareja1)
        db.add(pareja2)
        parejas.extend([pareja1, pareja2])
    
    db.commit()
    
    # Obtener todas las parejas creadas con la información de los jugadores
    parejas = db.query(ParejaPartida).filter(
        ParejaPartida.campeonato_id == campeonato_id,
        ParejaPartida.partida == partida
    ).order_by(
        ParejaPartida.mesa,
        ParejaPartida.numero_pareja
    ).all()
    
    # Cargar la información de los jugadores
    for pareja in parejas:
        pareja.jugador1 = db.query(Jugador).filter(Jugador.id == pareja.jugador1_id).first()
        pareja.jugador2 = db.query(Jugador).filter(Jugador.id == pareja.jugador2_id).first()
    
    return parejas 

@router.post("/corregir-estado-campeonato/{campeonato_id}")
async def corregir_estado_campeonato(campeonato_id: int, db: Session = Depends(get_db)):
    """Corrige el estado del campeonato basado en los datos reales de parejas_partida"""
    try:
        # Obtener la última partida que tiene parejas asignadas
        ultima_partida = db.query(func.max(ParejaPartida.partida)).filter(
            ParejaPartida.campeonato_id == campeonato_id
        ).scalar()

        if ultima_partida is None:
            raise HTTPException(status_code=404, detail="No se encontraron partidas para este campeonato")

        # Actualizar el campeonato con la partida actual correcta
        campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
        if not campeonato:
            raise HTTPException(status_code=404, detail="Campeonato no encontrado")

        campeonato.partida_actual = ultima_partida
        db.commit()

        return {
            "message": "Estado del campeonato corregido",
            "partida_actual": ultima_partida
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/actualizar-partida-actual/{campeonato_id}/{partida}")
async def actualizar_partida_actual(campeonato_id: int, partida: int, db: Session = Depends(get_db)):
    """Actualiza manualmente la partida actual del campeonato"""
    try:
        campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
        if not campeonato:
            raise HTTPException(status_code=404, detail="Campeonato no encontrado")

        campeonato.partida_actual = partida
        db.commit()

        return {
            "message": "Partida actual actualizada correctamente",
            "partida_actual": partida
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 