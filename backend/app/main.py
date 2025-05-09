from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import jugador, campeonato, pareja_partida, resultado, mesa, partida
import uvicorn
import os
from dotenv import load_dotenv
from app.db.base import Base, engine
from sqlalchemy import text
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

def init_db():
    try:
        # Intentar crear las tablas si no existen
        Base.metadata.create_all(bind=engine)
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {str(e)}")
        # No levantar la excepción para permitir que la app funcione incluso si hay error
        # En desarrollo, la base de datos ya podría existir

# Inicializar la base de datos
init_db()

app = FastAPI(
    title="API de Dominó",
    description="API para gestionar campeonatos de dominó",
    version="1.0.0"
)

# Configurar CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
debug_mode = os.getenv("DEBUG", "False").lower() == "true"

# En modo debug, permitir todos los orígenes
if debug_mode:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar codificación UTF-8 para las respuestas
@app.middleware("http")
async def add_charset_middleware(request, call_next):
    response = await call_next(request)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

# Manejador de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers={
            "Access-Control-Allow-Origin": "*" if debug_mode else origins[0],
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Incluir rutas
app.include_router(jugador.router, prefix="/api", tags=["jugadores"])
app.include_router(campeonato.router, prefix="/api", tags=["campeonatos"])
app.include_router(pareja_partida.router, prefix="/api", tags=["parejas_partida"])
app.include_router(resultado.router, prefix="/api", tags=["resultados"])
app.include_router(mesa.router, prefix="/api", tags=["mesas"])
app.include_router(partida.router, prefix="/api", tags=["partidas"])

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Domino Parejas Individual"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 