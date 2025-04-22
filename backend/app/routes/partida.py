from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.resultado import Resultado
from app.models.pareja_partida import ParejaPartida
from sqlalchemy import func
from app.models.campeonato import Campeonato
from app.models.jugador import Jugador
from typing import List, Dict
from app.schemas.resultado import Resultado as ResultadoSchema

router = APIRouter(
    prefix="/partidas",
    tags=["partidas"]
)

@router.post("/cerrar/{campeonato_id}/{partida}")
async def cerrar_partida(campeonato_id: int, partida: int, db: Session = Depends(get_db)):
    """Cierra la partida actual y prepara la siguiente"""
    try:
        # 1. Verificar que el campeonato existe
        campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
        if not campeonato:
            raise HTTPException(status_code=404, detail="Campeonato no encontrado")

        # 2. Verificar que la partida es válida
        if partida != campeonato.partida_actual:
            raise HTTPException(status_code=400, detail="La partida especificada no es la partida actual")

        # 3. Verificar que todas las mesas tienen resultados registrados
        mesas = db.query(ParejaPartida.mesa).filter(
            ParejaPartida.campeonato_id == campeonato_id,
            ParejaPartida.partida == partida
        ).distinct().all()
        
        mesas_ids = [mesa[0] for mesa in mesas]
        
        for mesa_id in mesas_ids:
            resultados = db.query(Resultado).filter(
                Resultado.campeonato_id == campeonato_id,
                Resultado.partida == partida,
                Resultado.mesa == mesa_id
            ).all()
            
            if not resultados:
                raise HTTPException(
                    status_code=400,
                    detail=f"La mesa {mesa_id} no tiene resultados registrados"
                )

        # 4. Calcular el ranking actualizado
        resultados = db.query(
            Resultado.jugador_id,
            func.sum(Resultado.PG).label('total_PG'),
            func.sum(Resultado.PC).label('total_PC'),
            func.sum(Resultado.PT).label('total_PT'),
            func.sum(Resultado.MG).label('total_MG')
        ).filter(
            Resultado.campeonato_id == campeonato_id,
            Resultado.partida <= partida
        ).group_by(
            Resultado.jugador_id
        ).order_by(
            func.sum(Resultado.PG).desc(),  # Primero por PG descendente
            func.sum(Resultado.PC).desc(),  # Segundo por PC descendente
            func.sum(Resultado.PT).desc(),  # Tercero por PT descendente
            func.sum(Resultado.MG),         # Cuarto por MG ascendente
            Resultado.jugador_id.asc()      # Quinto por ID para desempate consistente
        ).all()

        # Crear el ranking
        ranking = []
        for r in resultados:
            jugador = db.query(Jugador).filter(Jugador.id == r.jugador_id).first()
            if jugador and jugador.activo:
                ranking.append({
                    'jugador_id': r.jugador_id,
                    'PG': r.total_PG,
                    'PC': r.total_PC,
                    'PT': r.total_PT,
                    'MG': r.total_MG
                })

        # 5. Si no es la última partida, crear parejas para la siguiente
        if partida < campeonato.numero_partidas:
            # Obtener los IDs de jugadores ordenados por ranking
            jugadores_ordenados = [r['jugador_id'] for r in ranking]
            
            # Obtener jugadores activos que no tienen resultados
            jugadores_activos = db.query(Jugador).filter(
                Jugador.campeonato_id == campeonato_id,
                Jugador.activo == True
            ).all()
            
            jugadores_activos_ids = [j.id for j in jugadores_activos]
            jugadores_sin_ranking = [j_id for j_id in jugadores_activos_ids if j_id not in jugadores_ordenados]
            
            # Agregar jugadores sin ranking al final
            jugadores_ordenados.extend(jugadores_sin_ranking)
            
            # Eliminar parejas existentes de la siguiente partida
            db.query(ParejaPartida).filter(
                ParejaPartida.campeonato_id == campeonato_id,
                ParejaPartida.partida == partida + 1
            ).delete()
            
            # Crear nuevas parejas según el ranking
            num_mesas = (len(jugadores_ordenados) + 3) // 4
            
            for mesa in range(num_mesas):
                # Índices base para esta mesa
                indice_base = mesa * 4
                
                # Pareja 1: jugador 1 y 3 de la mesa (según ranking)
                jugador1_idx = indice_base
                jugador2_idx = indice_base + 2
                
                # Crear primera pareja
                pareja1 = ParejaPartida(
                    partida=partida + 1,
                    mesa=mesa + 1,
                    jugador1_id=jugadores_ordenados[jugador1_idx] if jugador1_idx < len(jugadores_ordenados) else None,
                    jugador2_id=jugadores_ordenados[jugador2_idx] if jugador2_idx < len(jugadores_ordenados) else None,
                    numero_pareja=1,
                    campeonato_id=campeonato_id
                )
                db.add(pareja1)
                
                # Pareja 2: jugador 2 y 4 de la mesa (según ranking)
                jugador3_idx = indice_base + 1
                jugador4_idx = indice_base + 3
                
                # Crear segunda pareja
                pareja2 = ParejaPartida(
                    partida=partida + 1,
                    mesa=mesa + 1,
                    jugador1_id=jugadores_ordenados[jugador3_idx] if jugador3_idx < len(jugadores_ordenados) else None,
                    jugador2_id=jugadores_ordenados[jugador4_idx] if jugador4_idx < len(jugadores_ordenados) else None,
                    numero_pareja=2,
                    campeonato_id=campeonato_id
                )
                db.add(pareja2)
            
            # Actualizar la partida actual
            campeonato.partida_actual = partida + 1
            
            db.commit()
            return {"mensaje": "Partida cerrada correctamente", "nueva_partida": partida + 1}
        else:
            # Si es la última partida, marcar el campeonato como finalizado
            campeonato.finalizado = True
            db.commit()
            return {"mensaje": "Campeonato finalizado", "nueva_partida": partida}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 