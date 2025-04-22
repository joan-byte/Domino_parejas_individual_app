from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .base_class import Base
import os
from dotenv import load_dotenv
from sqlalchemy.sql import text
import logging

# Cargar variables de entorno
load_dotenv()

# Importar todos los modelos para que SQLAlchemy los conozca
from app.models.jugador import Jugador
from app.models.campeonato import Campeonato
from app.models.resultado import Resultado
from app.models.mesa import Mesa
from app.models.pareja_partida import ParejaPartida

# Cargar variables de entorno directamente usando os.getenv y los defaults
# .env será cargado por load_dotenv()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "domino_parejas_individualdb")
DB_USER = os.getenv("DB_USER", "individual")
DB_PASS = os.getenv("DB_PASS", "375CheyTac") # Asegúrate que este default es seguro o elimina el default

# Construir la URL con las variables cargadas de .env o defaults
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print(f"Connecting to database with URL: {DATABASE_URL}") # Mantenemos este print para confirmar

# Crear el motor de la base de datos
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    # Configuración adicional para manejar la zona horaria y codificación
    connect_args={
        "options": "-c timezone=utc -c client_encoding=utf8",
        "client_encoding": "utf8"
    }
)

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def recreate_database():
    """Recrea todas las tablas en la base de datos."""
    try:
        # Usar SQLAlchemy para crear las tablas
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        logger.info("Base de datos recreada correctamente usando SQLAlchemy")
    except Exception as e:
        logger.error(f"Error al recrear la base de datos: {str(e)}")
        raise