from fastapi import APIRouter
from app.api.endpoints import campeonatos, jugadores
from app.routes import campeonato, jugador, pareja_partida, resultado, partida

api_router = APIRouter()
api_router.include_router(campeonatos.router, prefix="/campeonatos", tags=["campeonatos"])
api_router.include_router(jugadores.router, prefix="/jugadores", tags=["jugadores"])

router = APIRouter(
    prefix="/api/v1",
    tags=["api"]
)

router.include_router(campeonato.router)
router.include_router(jugador.router)
router.include_router(pareja_partida.router)
router.include_router(resultado.router)
router.include_router(partida.router) 