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

def get_env_value(env_name, default_value):
    # Primero intentar leer del archivo si existe la variable _FILE
    file_env = os.getenv(f"{env_name}_FILE")
    if file_env and os.path.exists(file_env):
        with open(file_env) as f:
            return f.read().strip()
    
    # Si no hay archivo o no se puede leer, usar la variable de entorno directa
    return os.getenv(env_name, default_value)

# Construir la URL de la base de datos usando la nueva función
DB_HOST = get_env_value("DB_HOST", "localhost")
DB_PORT = get_env_value("DB_PORT", "5432")
DB_NAME = get_env_value("DB_NAME", "domino_parejas_individualdb")
DB_USER = get_env_value("DB_USER", "individual")
DB_PASS = get_env_value("DB_PASS", "375CheyTac")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Crear el motor de la base de datos
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    # Configuración adicional para manejar la zona horaria
    connect_args={"options": "-c timezone=utc"}
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