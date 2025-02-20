from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.resultado import Resultado
from app.models.pareja_partida import ParejaPartida
from sqlalchemy import func
from app.models.campeonato import Campeonato

router = APIRouter(
    tags=["partidas"]
)

# El endpoint de cerrar partida se ha movido a pareja_partida.py para evitar duplicación 