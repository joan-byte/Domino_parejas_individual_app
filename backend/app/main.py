from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.core.config import settings
from app.routes import mesa, resultado, pareja_partida, jugador, campeonato, partida
from fastapi import APIRouter

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para la aplicación de Domino Parejas Individual",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
origins = [
    "http://localhost:5173",    # Frontend URL
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Registrar las rutas
logger.info("Registrando rutas de la API...")

# Crear el router principal con prefijo /api
api_router = APIRouter(prefix="/api")

# Incluir los sub-routers
api_router.include_router(mesa.router)
api_router.include_router(resultado.router)
api_router.include_router(pareja_partida.router)
api_router.include_router(jugador.router)
api_router.include_router(campeonato.router)
api_router.include_router(partida.router)

# Incluir el router principal en la aplicación
app.include_router(api_router)

logger.info("Todas las rutas han sido registradas")

@app.get("/")
async def root():
    logger.debug("Endpoint raíz llamado")
    return {"message": "Bienvenido a la API de Domino Parejas Individual"} 