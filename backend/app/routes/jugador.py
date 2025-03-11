from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List
from app.db.base import get_db
from app.models.jugador import Jugador
from app.schemas.jugador import JugadorCreate, JugadorResponse, JugadorUpdate
from app.models.resultado import Resultado
from app.models.pareja_partida import ParejaPartida

router = APIRouter(
    prefix="/jugadores",
    tags=["jugadores"]
)

@router.post("/", response_model=JugadorResponse)
async def create_jugador(jugador: JugadorCreate, db: Session = Depends(get_db)):
    """Crear un nuevo jugador"""
    # Verificar si ya existe un jugador con el mismo nombre y apellidos en el mismo campeonato
    existing_jugador = db.query(Jugador).filter(
        and_(
            Jugador.nombre == jugador.nombre,
            Jugador.apellidos == jugador.apellidos,
            Jugador.campeonato_id == jugador.campeonato_id
        )
    ).first()
    
    if existing_jugador:
        raise HTTPException(
            status_code=400,
            detail=f"El jugador {jugador.nombre} {jugador.apellidos} ya está inscrito en este campeonato"
        )
    
    # Obtener el último ID de jugador para este campeonato
    ultimo_jugador = db.query(Jugador).filter(
        Jugador.campeonato_id == jugador.campeonato_id
    ).order_by(Jugador.id.desc()).first()
    
    # Si no hay jugadores, empezar desde 1, si no, incrementar el último ID
    nuevo_id = 1 if not ultimo_jugador else ultimo_jugador.id + 1
    
    # Crear el jugador con los campos del esquema y establecer activo=True
    jugador_data = jugador.dict()
    jugador_data['activo'] = True  # Forzar activo=True al crear
    jugador_data['id'] = nuevo_id  # Asignar el nuevo ID
    db_jugador = Jugador(**jugador_data)
    
    try:
        db.add(db_jugador)
        db.commit()
        db.refresh(db_jugador)
        return db_jugador
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[JugadorResponse])
def read_jugadores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de jugadores"""
    jugadores = db.query(Jugador).offset(skip).limit(limit).all()
    return jugadores

@router.get("/{jugador_id}", response_model=JugadorResponse)
def read_jugador(jugador_id: int, db: Session = Depends(get_db)):
    """Obtener un jugador específico"""
    jugador = db.query(Jugador).filter(Jugador.id == jugador_id).first()
    if jugador is None:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    return jugador

@router.put("/{jugador_id}", response_model=JugadorResponse)
def update_jugador(jugador_id: int, jugador: JugadorUpdate, db: Session = Depends(get_db)):
    """Actualizar un jugador"""
    db_jugador = db.query(Jugador).filter(Jugador.id == jugador_id).first()
    if db_jugador is None:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    # Si se está actualizando nombre o apellidos, verificar que no exista otro jugador con esa combinación
    if (jugador.nombre is not None or jugador.apellidos is not None):
        nuevo_nombre = jugador.nombre if jugador.nombre is not None else db_jugador.nombre
        nuevo_apellidos = jugador.apellidos if jugador.apellidos is not None else db_jugador.apellidos
        
        existing_jugador = db.query(Jugador).filter(
            and_(
                Jugador.nombre == nuevo_nombre,
                Jugador.apellidos == nuevo_apellidos,
                Jugador.campeonato_id == db_jugador.campeonato_id,
                Jugador.id != jugador_id
            )
        ).first()
        
        if existing_jugador:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe otro jugador con el nombre {nuevo_nombre} {nuevo_apellidos} en este campeonato"
            )
    
    for key, value in jugador.dict(exclude_unset=True).items():
        setattr(db_jugador, key, value)
    
    db.commit()
    db.refresh(db_jugador)
    return db_jugador

@router.delete("/{jugador_id}")
def delete_jugador(jugador_id: int, db: Session = Depends(get_db)):
    """Eliminar un jugador"""
    db_jugador = db.query(Jugador).filter(Jugador.id == jugador_id).first()
    if db_jugador is None:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    db.delete(db_jugador)
    db.commit()
    return {"message": "Jugador eliminado"}

@router.get("/campeonato/{campeonato_id}", response_model=List[JugadorResponse])
async def get_jugadores_by_campeonato(campeonato_id: int, db: Session = Depends(get_db)):
    """Obtener jugadores de un campeonato específico"""
    jugadores = db.query(Jugador).filter(
        Jugador.campeonato_id == campeonato_id
    ).order_by(Jugador.id).all()
    return jugadores

@router.put("/{jugador_id}/toggle-activo", response_model=JugadorResponse)
async def toggle_jugador_activo(jugador_id: int, db: Session = Depends(get_db)):
    """Cambiar el estado activo/inactivo de un jugador"""
    # Obtener el jugador incluyendo el campeonato_id
    jugador = db.query(Jugador).filter(
        Jugador.id == jugador_id
    ).first()
    
    if not jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    try:
        estado_anterior = jugador.activo
        jugador.activo = not estado_anterior
        
        # Verificar si hay resultados o parejas asociadas antes de desactivar
        if not jugador.activo:
            # Verificar si el jugador está en alguna pareja
            parejas = db.query(ParejaPartida).filter(
                or_(
                    and_(
                        ParejaPartida.jugador1_id == jugador_id,
                        ParejaPartida.campeonato_id == jugador.campeonato_id
                    ),
                    and_(
                        ParejaPartida.jugador2_id == jugador_id,
                        ParejaPartida.campeonato_id == jugador.campeonato_id
                    )
                )
            ).first()
            
            if parejas:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="No se puede desactivar el jugador porque está asignado a una pareja"
                )
        
        db.commit()
        db.refresh(jugador)
        
        # Verificar que el cambio se aplicó correctamente
        if jugador.activo == estado_anterior:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Error al cambiar el estado del jugador: el cambio no se guardó correctamente"
            )
        
        return jugador
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activos/campeonato/{campeonato_id}", response_model=List[JugadorResponse])
async def get_jugadores_activos_by_campeonato(campeonato_id: int, db: Session = Depends(get_db)):
    """Obtener lista de jugadores activos de un campeonato específico"""
    jugadores = db.query(Jugador).filter(
        and_(
            Jugador.campeonato_id == campeonato_id,
            Jugador.activo == True
        )
    ).all()
    return jugadores

@router.put("/{jugador_id}/desactivar-y-quitar", response_model=dict)
async def desactivar_y_quitar_jugador(
    jugador_id: int,
    partida_actual: int = Body(...),
    campeonato_id: int = Body(...),
    db: Session = Depends(get_db)
):
    """Desactivar un jugador y quitarlo de las asignaciones de mesa pendientes"""
    # Verificar si el jugador existe y pertenece al campeonato
    jugador = db.query(Jugador).filter(
        and_(
            Jugador.id == jugador_id,
            Jugador.campeonato_id == campeonato_id
        )
    ).first()
    
    if not jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado en este campeonato")

    try:
        # Desactivar el jugador
        jugador.activo = False
        
        # Commit el cambio
        db.commit()
        db.refresh(jugador)
            
        return {
            "message": "Jugador desactivado correctamente",
            "jugador_id": jugador_id,
            "activo": False,
            "campeonato_id": campeonato_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    