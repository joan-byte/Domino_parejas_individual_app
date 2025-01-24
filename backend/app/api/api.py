from fastapi import APIRouter
from app.api.endpoints import campeonatos, jugadores

api_router = APIRouter()
api_router.include_router(campeonatos.router, prefix="/campeonatos", tags=["campeonatos"])
api_router.include_router(jugadores.router, prefix="/jugadores", tags=["jugadores"]) 