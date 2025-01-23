from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.core.config import settings
from app.routes import mesa, resultado, pareja_partida, jugador, campeonato

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para la aplicación de Domino Parejas Individual",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuración CORS
origins = [
    "http://localhost:5173",    # Vite dev server
    "http://127.0.0.1:5173",
    "http://localhost:8000",    # Backend FastAPI
    "http://127.0.0.1:8000"     # Backend FastAPI alternativo
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Incluir las rutas
logger.info("Registrando rutas de la API...")

# Incluir los routers sin prefijos adicionales
app.include_router(campeonato.router)
app.include_router(jugador.router)
app.include_router(mesa.router)
app.include_router(resultado.router)
app.include_router(pareja_partida.router)

logger.info("Todas las rutas han sido registradas")

@app.get("/")
async def root():
    logger.debug("Endpoint raíz llamado")
    return {"message": "Bienvenido a la API de Domino Parejas Individual"} 