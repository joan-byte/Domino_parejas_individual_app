from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import jugador, campeonato, pareja_partida, resultado, mesa
import uvicorn
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Forzar la URL de la base de datos correcta
os.environ["DATABASE_URL"] = "postgresql://individual:375CheyTac@localhost:5432/domino_parejas_individualdb"

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
app.include_router(jugador.router, prefix="/api")
app.include_router(campeonato.router, prefix="/api")
app.include_router(pareja_partida.router, prefix="/api")
app.include_router(resultado.router, prefix="/api")
app.include_router(mesa.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Domino Parejas Individual"}

if __name__ == "__main__":
    # Forzar el puerto 8000
    port = 8000
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True) 