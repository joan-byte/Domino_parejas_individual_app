from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import jugador, campeonato, pareja_partida, resultado, mesa
import uvicorn

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

# Configurar codificación UTF-8 para las respuestas
@app.middleware("http")
async def add_charset_middleware(request, call_next):
    response = await call_next(request)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

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
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 