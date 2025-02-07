from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.resultado import Resultado
from app.models.pareja_partida import ParejaPartida
from sqlalchemy import func

router = APIRouter(
    tags=["partidas"]
)

@router.post("/partidas/cerrar/{campeonato_id}/{partida}")
async def cerrar_partida(campeonato_id: int, partida: int, db: Session = Depends(get_db)):
    """Cierra la partida actual y prepara la siguiente"""
    
    # 1. Verificar que existen resultados para todas las mesas
    parejas = db.query(ParejaPartida).filter(
        ParejaPartida.campeonato_id == campeonato_id,
        ParejaPartida.partida == partida
    ).all()
    
    if not parejas:
        raise HTTPException(status_code=404, detail="No se encontraron parejas para esta partida")
    
    mesas = {pareja.mesa for pareja in parejas}
    
    # Verificar resultados para cada mesa
    for mesa in mesas:
        resultados_mesa = db.query(Resultado).filter(
            Resultado.campeonato_id == campeonato_id,
            Resultado.partida == partida,
            Resultado.mesa == mesa
        ).all()
        
        if not resultados_mesa:
            raise HTTPException(
                status_code=400, 
                detail=f"La mesa {mesa} no tiene resultados registrados"
            )
    
    # 2. Obtener el ranking actualizado
    ranking = db.query(
        Resultado.jugador_id,
        func.sum(Resultado.PG).label('total_PG'),
        func.sum(Resultado.PC).label('total_PC'),
        func.sum(Resultado.PT).label('total_PT')
    ).filter(
        Resultado.campeonato_id == campeonato_id,
        Resultado.partida <= partida
    ).group_by(
        Resultado.jugador_id
    ).order_by(
        func.sum(Resultado.PG).desc(),
        func.sum(Resultado.PC).desc(),
        func.sum(Resultado.PT).desc()
    ).all()
    
    if not ranking:
        raise HTTPException(status_code=404, detail="No se encontraron resultados para calcular el ranking")
    
    # 3. Crear las parejas para la siguiente partida
    jugadores_ordenados = [r[0] for r in ranking]
    nueva_partida = partida + 1
    nuevas_parejas = []
    
    # Crear parejas según el ranking
    for i in range(0, len(jugadores_ordenados), 4):
        if i + 3 >= len(jugadores_ordenados):
            break
            
        mesa = (i // 4) + 1
        
        # Pareja 1: jugador ranking 1 y 3
        pareja1 = ParejaPartida(
            partida=nueva_partida,
            mesa=mesa,
            jugador1_id=jugadores_ordenados[i],      # Ranking 1
            jugador2_id=jugadores_ordenados[i + 2],  # Ranking 3
            numero_pareja=1,
            campeonato_id=campeonato_id
        )
        
        # Pareja 2: jugador ranking 2 y 4
        pareja2 = ParejaPartida(
            partida=nueva_partida,
            mesa=mesa,
            jugador1_id=jugadores_ordenados[i + 1],  # Ranking 2
            jugador2_id=jugadores_ordenados[i + 3],  # Ranking 4
            numero_pareja=2,
            campeonato_id=campeonato_id
        )
        
        db.add(pareja1)
        db.add(pareja2)
        nuevas_parejas.extend([pareja1, pareja2])
    
    db.commit()
    
    return {"message": "Partida cerrada y nuevas parejas asignadas correctamente"} 