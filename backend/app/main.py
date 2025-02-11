from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import campeonato, jugador, pareja_partida, resultado, mesa

app = FastAPI(
    title="API de Dominó",
    description="API para gestionar campeonatos de dominó",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(campeonato.router, prefix="/api")
app.include_router(jugador.router, prefix="/api")
app.include_router(pareja_partida.router, prefix="/api")
app.include_router(resultado.router, prefix="/api")
app.include_router(mesa.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Domino Parejas Individual"} 