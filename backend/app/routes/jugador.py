from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
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
    jugador = db.query(Jugador).filter(Jugador.id == jugador_id).first()
    if not jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    jugador.activo = not jugador.activo
    db.commit()
    db.refresh(jugador)
    return jugador

@router.put("/{jugador_id}/desactivar-y-quitar", response_model=dict)
async def desactivar_y_quitar_jugador(jugador_id: int, partida_actual: int, campeonato_id: int, db: Session = Depends(get_db)):
    """
    Desactiva un jugador y lo quita de su pareja y mesa si no tiene resultados registrados
    en la partida actual.
    """
    # Verificar si el jugador existe
    jugador = db.query(Jugador).filter(Jugador.id == jugador_id, Jugador.campeonato_id == campeonato_id).first()
    if not jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    # Verificar si el jugador tiene resultados en la partida actual
    resultados = db.query(Resultado).filter(
        Resultado.jugador_id == jugador_id,
        Resultado.partida == partida_actual,
        Resultado.campeonato_id == campeonato_id
    ).first()
    
    if resultados:
        # Si tiene resultados, solo desactivar
        jugador.activo = False
        db.commit()
        db.refresh(jugador)
        return {
            "mensaje": "El jugador ha sido desactivado pero no se ha quitado de su mesa porque ya tiene resultados registrados",
            "solo_desactivado": True,
            "jugador": jugador
        }
    
    # Si no tiene resultados, buscar la pareja a la que pertenece
    pareja_como_jugador1 = db.query(ParejaPartida).filter(
        ParejaPartida.jugador1_id == jugador_id,
        ParejaPartida.partida == partida_actual,
        ParejaPartida.campeonato_id == campeonato_id
    ).first()
    
    pareja_como_jugador2 = db.query(ParejaPartida).filter(
        ParejaPartida.jugador2_id == jugador_id,
        ParejaPartida.partida == partida_actual,
        ParejaPartida.campeonato_id == campeonato_id
    ).first()
    
    pareja = pareja_como_jugador1 or pareja_como_jugador2
    
    if not pareja:
        # Si no está en ninguna pareja, solo desactivar
        jugador.activo = False
        db.commit()
        db.refresh(jugador)
        return {
            "mensaje": "El jugador ha sido desactivado (no estaba asignado a ninguna mesa)",
            "solo_desactivado": True,
            "jugador": jugador
        }
    
    # Guardar información de la mesa y pareja
    mesa_num = pareja.mesa
    pareja_num = pareja.numero_pareja
    
    # Independientemente de si es jugador1 o jugador2, lo quitamos de la pareja
    if pareja_como_jugador1:
        # Si es jugador1, simplemente establecemos jugador1_id a NULL
        # Nota: Esto podría requerir modificar la restricción NOT NULL en la base de datos
        # Como alternativa, si jugador1_id no puede ser NULL, eliminamos la pareja
        if pareja.jugador2_id:
            # Si hay un jugador2, lo movemos a la posición de jugador1
            pareja.jugador1_id = pareja.jugador2_id
            pareja.jugador2_id = None
        else:
            # Si no hay jugador2 y estamos quitando jugador1, la pareja quedaría vacía
            # En este caso, eliminamos la pareja
            db.delete(pareja)
    elif pareja_como_jugador2:
        # Si es jugador2, simplemente lo establecemos a NULL
        pareja.jugador2_id = None
    
    # Desactivar al jugador
    jugador.activo = False
    
    db.commit()
    
    # Si la pareja no fue eliminada, refrescarla
    if not (pareja_como_jugador1 and pareja.jugador2_id is None):
        db.refresh(pareja)
    
    return {
        "mensaje": f"El jugador ha sido desactivado y quitado de la mesa {mesa_num}, pareja {pareja_num}",
        "solo_desactivado": False,
        "jugador": jugador,
        "mesa": mesa_num,
        "pareja": pareja_num
    }
    