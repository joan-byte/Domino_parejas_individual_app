from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import random
from app.db.base import get_db
from app.models.pareja_partida import ParejaPartida
from app.models.resultado import Resultado
from app.schemas.pareja_partida import (
    ParejaPartidaSchema,
    ParejaPartidaCreate,
    ParejaNueva,
    AsignacionParejas,
    SorteoInicial,
    SiguientePartidaResponse,
    JugadorAsignadoSchema,
    MesaSchema
)
from app.models.jugador import Jugador
from app.models.campeonato import Campeonato
from app.schemas.jugador import JugadorResponse

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
    
    La asignación sigue el siguiente patrón:
    Mesa 1: Pareja 1 (1º y 3º) vs Pareja 2 (2º y 4º)
    Mesa 2: Pareja 1 (5º y 7º) vs Pareja 2 (6º y 8º)
    Mesa 3: Pareja 1 (9º y 11º) vs Pareja 2 (10º y 12º)
    Y así sucesivamente...
    """
    try:
        # Obtener la última partida asignada
        ultima_partida = db.query(func.max(ParejaPartida.partida)).filter(
            ParejaPartida.campeonato_id == campeonato_id
        ).scalar()
        
        siguiente_partida = (ultima_partida + 1) if ultima_partida is not None else 1

        # Verificar que el campeonato existe
        campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
        if not campeonato:
            raise HTTPException(status_code=404, detail="Campeonato no encontrado")
        
        # Obtener solo jugadores activos
        jugadores_activos = db.query(Jugador.id).filter(
            Jugador.campeonato_id == campeonato_id,
            Jugador.activo == True
        ).all()
        
        if not jugadores_activos:
            raise HTTPException(status_code=400, detail="No hay jugadores activos disponibles")
            
        jugadores_activos_ids = [j[0] for j in jugadores_activos]
        
        # Obtener el ranking actual usando los criterios correctos
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

        # Si no hay ranking, obtener jugadores en orden aleatorio
        if not ranking:
            jugadores_ordenados = [j[0] for j in jugadores_activos]
            random.shuffle(jugadores_ordenados)
        else:
            jugadores_ordenados = [r[0] for r in ranking]

        parejas = []
        num_jugadores = len(jugadores_ordenados)
        num_mesas = (num_jugadores + 3) // 4  # Redondear hacia arriba
        
        # Crear parejas para todas las mesas
        for mesa in range(num_mesas):
            indice_base = mesa * 4
            
            # Pareja 1: jugadores en posiciones base y base+2 (1º y 3º, 5º y 7º, etc.)
            if indice_base < num_jugadores:
                pareja1 = ParejaPartida(
                    partida=siguiente_partida,
                    mesa=mesa + 1,
                    jugador1_id=jugadores_ordenados[indice_base],     # 1º, 5º, 9º...
                    jugador2_id=jugadores_ordenados[indice_base + 2] if indice_base + 2 < num_jugadores else None,
                    numero_pareja=1,
                    campeonato_id=campeonato_id
                )
                db.add(pareja1)
                parejas.append(pareja1)
            
            # Pareja 2: jugadores en posiciones base+1 y base+3 (2º y 4º, 6º y 8º, etc.)
            if indice_base + 1 < num_jugadores:
                pareja2 = ParejaPartida(
                    partida=siguiente_partida,
                    mesa=mesa + 1,
                    jugador1_id=jugadores_ordenados[indice_base + 1], # 2º, 6º, 10º...
                    jugador2_id=jugadores_ordenados[indice_base + 3] if indice_base + 3 < num_jugadores else None,
                    numero_pareja=2,
                    campeonato_id=campeonato_id
                )
                db.add(pareja2)
                parejas.append(pareja2)

        db.commit()

        return SiguientePartidaResponse(
            mensaje="Parejas creadas correctamente",
            nueva_partida=siguiente_partida,
            parejas=parejas
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campeonato/{campeonato_id}/partida/{partida}", response_model=List[ParejaPartidaSchema])
def get_parejas_by_campeonato_partida(campeonato_id: int, partida: int, db: Session = Depends(get_db)):
    """Obtiene todas las parejas de un campeonato y partida específicos, solo con jugadores activos"""
    # Obtener todas las parejas para este campeonato y partida
    parejas = db.query(ParejaPartida).filter(
        ParejaPartida.campeonato_id == campeonato_id,
        ParejaPartida.partida == partida
    ).order_by(
        ParejaPartida.mesa,
        ParejaPartida.numero_pareja
    ).all()
    
    # Filtrar parejas para incluir solo jugadores activos
    parejas_filtradas = []
    for pareja in parejas:
        # Verificar si jugador1 está activo
        if pareja.jugador1 and pareja.jugador1.activo:
            # Si jugador2 existe, verificar si está activo
            if pareja.jugador2_id is None or (pareja.jugador2 and pareja.jugador2.activo):
                parejas_filtradas.append(pareja)
    
    return parejas_filtradas

@router.get("/mesas/{campeonato_id}/{partida}", response_model=List[MesaSchema])
def get_mesas_by_campeonato_partida(campeonato_id: int, partida: int, db: Session = Depends(get_db)):
    """Obtiene todas las mesas con sus parejas para un campeonato y partida específicos"""
    try:
        # Obtener los resultados existentes para esta partida
        resultados = db.query(Resultado).filter(
            Resultado.campeonato_id == campeonato_id,
            Resultado.partida == partida
        ).all()
        
        # Crear un conjunto de mesas con resultados y jugadores con resultados
        mesas_con_resultados = {resultado.mesa for resultado in resultados}
        jugadores_con_resultados = {(resultado.mesa, resultado.jugador_id) for resultado in resultados}
        
        # Obtener todas las parejas para este campeonato y partida
        parejas = db.query(ParejaPartida).filter(
            ParejaPartida.campeonato_id == campeonato_id,
            ParejaPartida.partida == partida
        ).order_by(
            ParejaPartida.mesa,
            ParejaPartida.numero_pareja
        ).all()
        
        # Filtrar parejas según los resultados y estado de los jugadores
        parejas_filtradas = []
        for pareja in parejas:
            # Si la mesa ya tiene resultados, incluir la pareja completa
            if pareja.mesa in mesas_con_resultados:
                parejas_filtradas.append(pareja)
                continue
            
            # Si no hay resultados, verificar cada jugador
            pareja_modificada = ParejaPartida(
                id=pareja.id,
                campeonato_id=pareja.campeonato_id,
                partida=pareja.partida,
                mesa=pareja.mesa,
                numero_pareja=pareja.numero_pareja
            )
            
            # Verificar jugador1
            if pareja.jugador1 and pareja.jugador1.activo:
                pareja_modificada.jugador1_id = pareja.jugador1_id
                pareja_modificada.jugador1 = pareja.jugador1
            else:
                pareja_modificada.jugador1_id = None
                pareja_modificada.jugador1 = None
            
            # Verificar jugador2
            if pareja.jugador2 and pareja.jugador2.activo:
                pareja_modificada.jugador2_id = pareja.jugador2_id
                pareja_modificada.jugador2 = pareja.jugador2
            else:
                pareja_modificada.jugador2_id = None
                pareja_modificada.jugador2 = None
            
            # Solo incluir la pareja si al menos tiene un jugador activo
            if pareja_modificada.jugador1_id is not None or pareja_modificada.jugador2_id is not None:
                parejas_filtradas.append(pareja_modificada)
        
        # Agrupar parejas por mesa
        mesas_dict = {}
        for pareja in parejas_filtradas:
            if pareja.mesa not in mesas_dict:
                mesas_dict[pareja.mesa] = {
                    "numeroMesa": pareja.mesa,
                    "pareja1": None,
                    "pareja2": None
                }
            
            if pareja.numero_pareja == 1:
                mesas_dict[pareja.mesa]["pareja1"] = pareja
            elif pareja.numero_pareja == 2:
                mesas_dict[pareja.mesa]["pareja2"] = pareja
        
        # Convertir el diccionario a una lista ordenada por número de mesa
        mesas = [mesas_dict[mesa_num] for mesa_num in sorted(mesas_dict.keys())]
        
        print(f"Mesas procesadas para campeonato {campeonato_id}, partida {partida}:", 
              [{"mesa": m["numeroMesa"], 
                "pareja1": {"jugador1": m["pareja1"].jugador1.id if m["pareja1"] and m["pareja1"].jugador1 else None,
                           "jugador2": m["pareja1"].jugador2.id if m["pareja1"] and m["pareja1"].jugador2 else None} if m["pareja1"] else None,
                "pareja2": {"jugador1": m["pareja2"].jugador1.id if m["pareja2"] and m["pareja2"].jugador1 else None,
                           "jugador2": m["pareja2"].jugador2.id if m["pareja2"] and m["pareja2"].jugador2 else None} if m["pareja2"] else None} 
               for m in mesas])
        
        return mesas
        
    except Exception as e:
        print(f"Error en get_mesas_by_campeonato_partida: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener las mesas: {str(e)}"
        )

@router.get("/jugadores-sin-asignar/{campeonato_id}/{partida}", response_model=List[JugadorResponse])
def get_jugadores_sin_asignar(campeonato_id: int, partida: int, db: Session = Depends(get_db)):
    """Obtiene todos los jugadores activos que no están asignados a ninguna pareja en la partida actual"""
    # Obtener todos los jugadores activos del campeonato
    jugadores_activos = db.query(Jugador).filter(
        Jugador.campeonato_id == campeonato_id,
        Jugador.activo == True
    ).all()
    
    # Obtener los IDs de jugadores ya asignados a parejas en esta partida
    jugadores_asignados = db.query(ParejaPartida.jugador1_id).filter(
        ParejaPartida.campeonato_id == campeonato_id,
        ParejaPartida.partida == partida
    ).union_all(
        db.query(ParejaPartida.jugador2_id).filter(
            ParejaPartida.campeonato_id == campeonato_id,
            ParejaPartida.partida == partida,
            ParejaPartida.jugador2_id != None  # Excluir parejas con jugador2 nulo
        )
    ).all()
    
    jugadores_asignados_ids = {j[0] for j in jugadores_asignados}
    
    # Filtrar jugadores que no están asignados
    jugadores_sin_asignar = [j for j in jugadores_activos if j.id not in jugadores_asignados_ids]
    
    return jugadores_sin_asignar

@router.get("/jugadores-asignados/{campeonato_id}/{partida}", response_model=List[JugadorAsignadoSchema])
def get_jugadores_asignados(campeonato_id: int, partida: int, db: Session = Depends(get_db)):
    """Obtiene todos los jugadores activos asignados a parejas en la partida actual con información de su mesa y pareja"""
    # Obtener todas las parejas para este campeonato y partida
    parejas = db.query(ParejaPartida).filter(
        ParejaPartida.campeonato_id == campeonato_id,
        ParejaPartida.partida == partida
    ).all()
    
    jugadores_asignados = []
    
    for pareja in parejas:
        # Agregar jugador1 si está activo
        if pareja.jugador1 and pareja.jugador1.activo:
            jugadores_asignados.append({
                "id": pareja.jugador1.id,
                "nombre": pareja.jugador1.nombre,
                "apellidos": pareja.jugador1.apellidos,
                "club": pareja.jugador1.club,
                "mesa": pareja.mesa,
                "numero_pareja": pareja.numero_pareja
            })
        
        # Agregar jugador2 si existe y está activo
        if pareja.jugador2 and pareja.jugador2.activo:
            jugadores_asignados.append({
                "id": pareja.jugador2.id,
                "nombre": pareja.jugador2.nombre,
                "apellidos": pareja.jugador2.apellidos,
                "club": pareja.jugador2.club,
                "mesa": pareja.mesa,
                "numero_pareja": pareja.numero_pareja
            })
    
    # Ordenar por ID de jugador
    jugadores_asignados.sort(key=lambda x: x["id"])
    
    return jugadores_asignados

@router.post("/partidas/cerrar/{campeonato_id}/{partida}")
async def cerrar_partida(campeonato_id: int, partida: int, db: Session = Depends(get_db)):
    """Cierra una partida y actualiza la partida actual del campeonato."""
    try:
        # Verificar que el campeonato existe
        campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
        if not campeonato:
            raise HTTPException(status_code=404, detail="Campeonato no encontrado")

        # Verificar que la partida que se intenta cerrar es la partida actual
        if partida != campeonato.partida_actual:
            raise HTTPException(
                status_code=400,
                detail=f"Solo se puede cerrar la partida actual ({campeonato.partida_actual}). No se puede cerrar la partida {partida}"
            )

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

        # Obtener todos los jugadores activos que participaron en esta partida
        jugadores_participantes = set()
        for pareja in parejas:
            # Verificar si jugador1 está activo antes de agregarlo
            if pareja.jugador1_id and pareja.jugador1.activo:
                jugadores_participantes.add(pareja.jugador1_id)
            # Verificar si jugador2 está activo antes de agregarlo
            if pareja.jugador2_id and pareja.jugador2.activo:
                jugadores_participantes.add(pareja.jugador2_id)

        # Verificar si hay resultados para todos los jugadores activos de esta partida
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
        
        # Si todas las validaciones pasan, procedemos a actualizar el estado
        
        # Si es la última partida, finalizar el campeonato
        if partida >= campeonato.numero_partidas:
            campeonato.finalizado = True
            campeonato.partida_actual = partida  # Mantener la última partida como actual
            db.commit()
            return {"mensaje": "Campeonato finalizado", "nueva_partida": partida}
        
        # Si no es la última, crear la siguiente partida
        nueva_partida = partida + 1
        
        try:
            # Crear parejas para la siguiente partida basadas en el ranking
            # Primero creamos las parejas sin actualizar la partida actual
            response = crear_parejas_siguiente_partida(campeonato_id, partida, db)
            
            # Si la creación de parejas fue exitosa, ahora sí actualizamos la partida actual
            if response and response.parejas:
                campeonato.partida_actual = nueva_partida
                db.commit()
                return {"mensaje": "Partida cerrada correctamente", "nueva_partida": nueva_partida}
            else:
                raise HTTPException(
                    status_code=500,
                    detail="No se pudieron crear las parejas para la siguiente partida"
                )
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error al crear parejas para la siguiente partida: {str(e)}"
            )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

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
        Resultado.partida < partida,  # Solo considerar partidas anteriores
        Resultado.jugador_id.in_(  # Solo considerar jugadores activos
            db.query(Jugador.id).filter(
                Jugador.campeonato_id == campeonato_id,
                Jugador.activo == True
            )
        )
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
    
    # Si es la primera partida o no hay ranking, obtener jugadores activos ordenados por ID
    if not ranking_results:
        jugadores_ordenados = [j.id for j in db.query(Jugador).filter(
            Jugador.campeonato_id == campeonato_id,
            Jugador.activo == True
        ).order_by(Jugador.id).all()]
    else:
        # Extraer los IDs de los jugadores en el orden correcto
        jugadores_ordenados = [r[0] for r in ranking_results]
    
    if not jugadores_ordenados:
        raise HTTPException(status_code=404, detail="No se encontraron jugadores activos para realizar la asignación")
    
    # Eliminar las parejas existentes de esta partida
    db.query(ParejaPartida).filter(
        ParejaPartida.campeonato_id == campeonato_id,
        ParejaPartida.partida == partida
    ).delete()
    
    parejas = []
    num_jugadores = len(jugadores_ordenados)
    num_mesas = (num_jugadores + 3) // 4  # Redondear hacia arriba para incluir la última mesa
    
    # Crear todas las parejas siguiendo el mismo patrón para todas las mesas
    for mesa in range(num_mesas):
        indice_base = mesa * 4
        
        # Pareja 1: jugadores en posiciones base y base+2 (1º y 3º, 5º y 7º, etc.)
        pareja1 = ParejaPartida(
            partida=partida,
            mesa=mesa + 1,
            jugador1_id=jugadores_ordenados[indice_base],     # 1º, 5º, 9º...
            jugador2_id=jugadores_ordenados[indice_base + 2] if indice_base + 2 < num_jugadores else None,
            numero_pareja=1,
            campeonato_id=campeonato_id
        )
        db.add(pareja1)
        parejas.append(pareja1)
        
        # Solo crear pareja 2 si hay al menos un jugador más disponible
        if indice_base + 1 < num_jugadores:
            pareja2 = ParejaPartida(
                partida=partida,
                mesa=mesa + 1,
                jugador1_id=jugadores_ordenados[indice_base + 1],  # 2º, 6º, 10º...
                jugador2_id=jugadores_ordenados[indice_base + 3] if indice_base + 3 < num_jugadores else None,
                numero_pareja=2,
                campeonato_id=campeonato_id
            )
            db.add(pareja2)
            parejas.append(pareja2)
    
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

@router.get("/ultima-partida/{campeonato_id}")
def get_ultima_partida(campeonato_id: int, db: Session = Depends(get_db)):
    """Obtiene la última partida de un campeonato"""
    # Verificar que el campeonato existe
    campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
    if not campeonato:
        raise HTTPException(status_code=404, detail="Campeonato no encontrado")
    
    # Devolver la partida actual del campeonato
    return {"ultima_partida": campeonato.partida_actual} 