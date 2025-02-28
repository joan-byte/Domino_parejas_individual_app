from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.db.base import get_db
from app.models.resultado import Resultado
from app.models.jugador import Jugador
from app.models.pareja_partida import ParejaPartida
from app.models.campeonato import Campeonato
from app.schemas.resultado import ResultadoMesaInput, Resultado as ResultadoSchema
from sqlalchemy.sql import func

router = APIRouter(
    tags=["resultados"]
)

def calcular_PV(PT: int, PM: int) -> int:
    """Calcula los Puntos Válidos (máximo PM del campeonato)"""
    return min(PT, PM)

@router.post("/resultados/mesa/", response_model=List[ResultadoSchema])
def create_resultados_mesa(datos: ResultadoMesaInput, db: Session = Depends(get_db)):
    # Obtener el PM del campeonato
    campeonato = db.query(Campeonato).filter(Campeonato.id == datos.campeonato_id).first()
    if not campeonato:
        raise HTTPException(status_code=404, detail="Campeonato no encontrado")
    
    # Verificar si es la última mesa de la partida
    ultima_mesa = db.query(func.max(ParejaPartida.mesa)).filter(
        ParejaPartida.campeonato_id == datos.campeonato_id,
        ParejaPartida.partida == datos.partida
    ).scalar()
    
    es_ultima_mesa = datos.mesa == ultima_mesa
    
    # Validar que los datos coincidan con es_ultima_mesa
    if es_ultima_mesa != datos.es_ultima_mesa:
        raise HTTPException(
            status_code=400, 
            detail="El indicador es_ultima_mesa no coincide con la mesa actual"
        )
    
    # Si no es la última mesa, validar que tenga 4 jugadores
    if not es_ultima_mesa:
        if not all([datos.jugador1_id, datos.jugador2_id, datos.jugador3_id, datos.jugador4_id]):
            raise HTTPException(
                status_code=400,
                detail="Las mesas que no son la última deben tener 4 jugadores"
            )
    
    # Inicializar lista de resultados
    resultados = []
    
    # Verificar si la última mesa está incompleta
    es_mesa_incompleta = es_ultima_mesa and (
        datos.jugador2_id is None or 
        datos.jugador3_id is None or 
        (datos.jugador3_id is not None and datos.jugador4_id is None)
    )
    
    if es_mesa_incompleta:
        # Calcular puntos automáticos para mesa incompleta
        PT_automatico = (campeonato.PM + 1) // 2  # Redondeo hacia arriba
        PV_automatico = PT_automatico
        PC_automatico = PT_automatico
        PG_automatico = 1
        MG_automatico = (PT_automatico + 29) // 30  # Redondeo hacia arriba
        
        # Crear resultados para todos los jugadores presentes con los mismos valores
        jugadores = [
            (1, datos.jugador1_id),
            (2, datos.jugador2_id),
            (3, datos.jugador3_id),
            (4, datos.jugador4_id)
        ]
        
        for num_jugador, jugador_id in jugadores:
            if jugador_id is not None:
                pareja = 1 if num_jugador <= 2 else 2
                resultado = Resultado(
                    partida=datos.partida,
                    mesa=datos.mesa,
                    jugador=num_jugador,
                    jugador_id=jugador_id,
                    pareja=pareja,
                    PT=PT_automatico,
                    PV=PV_automatico,
                    PC=PC_automatico,
                    PG=PG_automatico,
                    MG=MG_automatico,
                    campeonato_id=datos.campeonato_id
                )
                db.add(resultado)
                resultados.append(resultado)
    else:
        # Proceder con la lógica normal para mesas completas
        # Calcular puntos para la primera pareja
        PT_pareja1 = datos.puntos_pareja1
        PV_pareja1 = min(PT_pareja1, campeonato.PM)
        
        # Calcular puntos para la segunda pareja si existe
        PT_pareja2 = datos.puntos_pareja2 if datos.puntos_pareja2 is not None else 0
        PV_pareja2 = min(PT_pareja2, campeonato.PM) if datos.puntos_pareja2 is not None else 0
        
        # Calcular PC y PG para ambas parejas
        if datos.jugador3_id is not None:  # Si hay al menos un jugador en la segunda pareja
            PC_pareja1 = PV_pareja1 - PV_pareja2
            PC_pareja2 = PV_pareja2 - PV_pareja1
            PG_pareja1 = 1 if PC_pareja1 > 0 else 0
            PG_pareja2 = 1 if PC_pareja2 > 0 else 0
        else:  # Si no hay segunda pareja (solo posible en última mesa completa)
            if not es_ultima_mesa:
                raise HTTPException(
                    status_code=400,
                    detail="Solo la última mesa puede tener una sola pareja"
                )
            PC_pareja1 = PV_pareja1
            PG_pareja1 = 1
            PC_pareja2 = 0
            PG_pareja2 = 0
        
        # Crear resultados para la primera pareja
        resultado = Resultado(
            partida=datos.partida,
            mesa=datos.mesa,
            jugador=1,
            jugador_id=datos.jugador1_id,
            pareja=1,
            PT=PT_pareja1,
            PV=PV_pareja1,
            PC=PC_pareja1,
            PG=PG_pareja1,
            MG=datos.manos_ganadas_pareja1,
            campeonato_id=datos.campeonato_id
        )
        db.add(resultado)
        resultados.append(resultado)
        
        if datos.jugador2_id is not None:
            resultado = Resultado(
                partida=datos.partida,
                mesa=datos.mesa,
                jugador=2,
                jugador_id=datos.jugador2_id,
                pareja=1,
                PT=PT_pareja1,
                PV=PV_pareja1,
                PC=PC_pareja1,
                PG=PG_pareja1,
                MG=datos.manos_ganadas_pareja1,
                campeonato_id=datos.campeonato_id
            )
            db.add(resultado)
            resultados.append(resultado)
        elif not es_ultima_mesa:
            raise HTTPException(
                status_code=400,
                detail="Las mesas que no son la última deben tener pareja completa"
            )
        
        # Crear resultados para la segunda pareja si existe
        if datos.jugador3_id is not None:
            resultado = Resultado(
                partida=datos.partida,
                mesa=datos.mesa,
                jugador=3,
                jugador_id=datos.jugador3_id,
                pareja=2,
                PT=PT_pareja2,
                PV=PV_pareja2,
                PC=PC_pareja2,
                PG=PG_pareja2,
                MG=datos.manos_ganadas_pareja2 or 0,
                campeonato_id=datos.campeonato_id
            )
            db.add(resultado)
            resultados.append(resultado)
            
            if datos.jugador4_id is not None:
                resultado = Resultado(
                    partida=datos.partida,
                    mesa=datos.mesa,
                    jugador=4,
                    jugador_id=datos.jugador4_id,
                    pareja=2,
                    PT=PT_pareja2,
                    PV=PV_pareja2,
                    PC=PC_pareja2,
                    PG=PG_pareja2,
                    MG=datos.manos_ganadas_pareja2 or 0,
                    campeonato_id=datos.campeonato_id
                )
                db.add(resultado)
                resultados.append(resultado)
            elif not es_ultima_mesa:
                raise HTTPException(
                    status_code=400,
                    detail="Las mesas que no son la última deben tener parejas completas"
                )
        elif not es_ultima_mesa:
            raise HTTPException(
                status_code=400,
                detail="Las mesas que no son la última deben tener dos parejas"
            )
    
    try:
        db.commit()
        for resultado in resultados:
            db.refresh(resultado)
        return resultados
    except Exception as e:
        db.rollback()
        print(f"Error al guardar resultados: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al guardar resultados: {str(e)}")

@router.get("/resultados/", response_model=List[ResultadoSchema])
def read_resultados(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    resultados = db.query(Resultado).offset(skip).limit(limit).all()
    return resultados

@router.get("/resultados/campeonato/{campeonato_id}/partida/{partida}", response_model=List[ResultadoSchema])
def read_resultados_by_campeonato_partida(campeonato_id: int, partida: int, db: Session = Depends(get_db)):
    """Obtiene todos los resultados de una partida en un campeonato"""
    try:
        resultados = db.query(
            Resultado.id,
            Resultado.partida,
            Resultado.mesa,
            Resultado.jugador,
            Resultado.jugador_id,
            Resultado.pareja,
            Resultado.PT,
            Resultado.PV,
            Resultado.PC,
            Resultado.PG,
            Resultado.MG,
            Resultado.campeonato_id
        ).join(
            Jugador, Resultado.jugador_id == Jugador.id
        ).filter(
            Resultado.campeonato_id == campeonato_id,
            Resultado.partida == partida
        ).order_by(Resultado.mesa, Resultado.jugador).all()
        
        return resultados
    except Exception as e:
        print(f"Error en read_resultados_by_campeonato_partida: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener resultados: {str(e)}")

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
    
    # Obtener el PM del campeonato
    campeonato = db.query(Campeonato).filter(Campeonato.id == datos.campeonato_id).first()
    if not campeonato:
        raise HTTPException(status_code=404, detail="Campeonato no encontrado")
    
    # Calcular los nuevos valores usando el PM del campeonato
    PV_pareja1 = calcular_PV(datos.puntos_pareja1, campeonato.PM)
    PV_pareja2 = calcular_PV(datos.puntos_pareja2, campeonato.PM)
    
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
            resultado.MG = datos.manos_ganadas_pareja1
            resultado.pareja = 1  # Asegurar que el número de pareja es correcto
        else:  # Pareja 2
            resultado.PT = datos.puntos_pareja2
            resultado.PV = PV_pareja2
            resultado.PC = PC_pareja2
            resultado.PG = PG_pareja2
            resultado.MG = datos.manos_ganadas_pareja2
            resultado.pareja = 2  # Asegurar que el número de pareja es correcto
    
    db.commit()
    for resultado in resultados:
        db.refresh(resultado)
    
    return resultados

@router.get("/resultados/ranking/campeonato/{campeonato_id}")
async def get_ranking_campeonato(campeonato_id: int, partida: int = None, db: Session = Depends(get_db)):
    """Obtiene el ranking de jugadores de un campeonato hasta una partida específica.
    Si la partida especificada no tiene resultados, muestra los resultados hasta la última partida completada."""
    
    try:
        # Primero obtenemos todos los jugadores del sorteo inicial
        jugadores_sorteo = db.query(
            ParejaPartida.jugador1_id.label('jugador_id'),
            Jugador.nombre,
            Jugador.apellidos,
            Jugador.club
        ).join(
            Jugador, ParejaPartida.jugador1_id == Jugador.id
        ).filter(
            ParejaPartida.campeonato_id == campeonato_id,
            ParejaPartida.partida == 1
        ).union(
            db.query(
                ParejaPartida.jugador2_id.label('jugador_id'),
                Jugador.nombre,
                Jugador.apellidos,
                Jugador.club
            ).join(
                Jugador, ParejaPartida.jugador2_id == Jugador.id
            ).filter(
                ParejaPartida.campeonato_id == campeonato_id,
                ParejaPartida.partida == 1
            )
        ).order_by('jugador_id').all()

        if not jugadores_sorteo:
            raise HTTPException(status_code=404, detail="No se encontraron jugadores para este campeonato")

        # Si se especifica una partida, verificar si tiene resultados
        if partida is not None:
            resultados_partida = db.query(
                Resultado.id,
                Resultado.partida,
                Resultado.jugador_id
            ).filter(
                Resultado.campeonato_id == campeonato_id,
                Resultado.partida == partida
            ).first()
            
            if not resultados_partida:
                ultima_partida = db.query(func.max(Resultado.partida)).filter(
                    Resultado.campeonato_id == campeonato_id
                ).scalar()
                
                if ultima_partida:
                    partida = ultima_partida

        # Construir la consulta base para los resultados
        resultados_query = db.query(
            Resultado.jugador_id,
            func.sum(Resultado.PT).label('PT'),
            func.sum(Resultado.PG).label('PG'),
            func.sum(Resultado.PC).label('PC'),
            func.sum(Resultado.MG).label('MG'),
            func.max(Resultado.partida).label('ultima_partida')
        ).filter(
            Resultado.campeonato_id == campeonato_id
        )

        # Filtrar hasta la partida correspondiente si se especifica
        if partida is not None:
            resultados_query = resultados_query.filter(Resultado.partida <= partida)

        # Agrupar por jugador y obtener resultados
        resultados = resultados_query.group_by(
            Resultado.jugador_id
        ).all()

        # Creamos un diccionario con los resultados para acceso rápido
        resultados_dict = {r.jugador_id: r for r in resultados}

        # Combinamos la información
        ranking_list = []
        for jugador in jugadores_sorteo:
            resultados_jugador = resultados_dict.get(jugador.jugador_id)
            if resultados_jugador:
                ranking_list.append({
                    "jugador_id": jugador.jugador_id,
                    "nombre": jugador.nombre,
                    "apellidos": jugador.apellidos,
                    "club": jugador.club,
                    "PT": int(resultados_jugador.PT) if resultados_jugador.PT is not None else 0,
                    "PG": int(resultados_jugador.PG) if resultados_jugador.PG is not None else 0,
                    "PC": int(resultados_jugador.PC) if resultados_jugador.PC is not None else 0,
                    "MG": int(resultados_jugador.MG) if resultados_jugador.MG is not None else 0,
                    "ultima_partida": int(resultados_jugador.ultima_partida) if resultados_jugador.ultima_partida is not None else 0
                })
            else:
                # Si no hay resultados para el jugador, añadirlo con valores en 0
                ranking_list.append({
                    "jugador_id": jugador.jugador_id,
                    "nombre": jugador.nombre,
                    "apellidos": jugador.apellidos,
                    "club": jugador.club,
                    "PT": 0,
                    "PG": 0,
                    "PC": 0,
                    "MG": 0,
                    "ultima_partida": 0
                })

        # Ordenar el ranking por los criterios especificados
        ranking_list.sort(key=lambda x: (
            -x["PG"],      # Primero por PG descendente
            -x["PC"],      # Segundo por PC descendente
            -x["PT"],      # Tercero por PT descendente
            x["MG"],       # Cuarto por MG ascendente
            x["jugador_id"] # Quinto por ID del jugador para desempate consistente
        ))

        return ranking_list

    except Exception as e:
        print(f"Error en get_ranking_campeonato: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener el ranking: {str(e)}")

@router.get("/resultados/campeonato/{campeonato_id}/hasta-partida/{partida}", response_model=List[ResultadoSchema])
def read_resultados_hasta_partida(campeonato_id: int, partida: int, db: Session = Depends(get_db)):
    """Obtiene todos los resultados de un campeonato hasta una partida específica"""
    resultados = db.query(Resultado).filter(
        Resultado.campeonato_id == campeonato_id,
        Resultado.partida <= partida
    ).order_by(Resultado.partida, Resultado.mesa, Resultado.jugador).all()
    return resultados

@router.get("/resultados/debug/campeonato/{campeonato_id}/partida/{partida}")
async def debug_resultados_partida(campeonato_id: int, partida: int, db: Session = Depends(get_db)):
    """Endpoint de depuración para verificar los resultados de una partida específica"""
    try:
        # Obtener todos los resultados de la partida
        resultados = db.query(
            Resultado.jugador_id,
            Resultado.mesa,
            Resultado.PT,
            Resultado.PV,
            Resultado.PC,
            Resultado.PG,
            Resultado.MG,
            Jugador.nombre,
            Jugador.apellidos
        ).join(
            Jugador, Resultado.jugador_id == Jugador.id
        ).filter(
            Resultado.campeonato_id == campeonato_id,
            Resultado.partida == partida
        ).order_by(
            Resultado.mesa,
            Resultado.jugador
        ).all()

        # Formatear los resultados para mejor visualización
        resultados_formateados = []
        for r in resultados:
            resultados_formateados.append({
                "mesa": r.mesa,
                "jugador_id": r.jugador_id,
                "nombre": f"{r.nombre} {r.apellidos}",
                "PT": r.PT,
                "PV": r.PV,
                "PC": r.PC,
                "PG": r.PG,
                "MG": r.MG
            })

        return {
            "campeonato_id": campeonato_id,
            "partida": partida,
            "total_resultados": len(resultados),
            "resultados": resultados_formateados
        }

    except Exception as e:
        print(f"Error en debug_resultados_partida: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener los resultados: {str(e)}") 