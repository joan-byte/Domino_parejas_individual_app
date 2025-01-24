from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .base_class import Base
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar todos los modelos para que SQLAlchemy los conozca
from app.models.jugador import Jugador
from app.models.campeonato import Campeonato
from app.models.resultado import Resultado
from app.models.mesa import Mesa
from app.models.pareja_partida import ParejaPartida

# Crear el motor de la base de datos
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()