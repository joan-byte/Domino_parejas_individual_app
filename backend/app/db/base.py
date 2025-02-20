from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .base_class import Base
import os
from dotenv import load_dotenv
from sqlalchemy.sql import text

# Cargar variables de entorno
load_dotenv()

# Importar todos los modelos para que SQLAlchemy los conozca
from app.models.jugador import Jugador
from app.models.campeonato import Campeonato
from app.models.resultado import Resultado
from app.models.mesa import Mesa
from app.models.pareja_partida import ParejaPartida

# Forzar la URL de la base de datos correcta
DATABASE_URL = "postgresql://individual:375CheyTac@localhost:5432/domino_parejas_individualdb"

# Verificar que la URL no contenga "db" como host
if "db" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("@db:", "@localhost:")

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
    with engine.connect() as connection:
        # Eliminar tablas existentes
        connection.execute(text("""
            DROP TABLE IF EXISTS resultados CASCADE;
            DROP TABLE IF EXISTS resultado CASCADE;
            DROP TABLE IF EXISTS parejas_partida CASCADE;
            DROP TABLE IF EXISTS pareja_partida CASCADE;
            DROP TABLE IF EXISTS mesas CASCADE;
            DROP TABLE IF EXISTS jugador_campeonato CASCADE;
            DROP TABLE IF EXISTS jugadores CASCADE;
            DROP TABLE IF EXISTS campeonatos CASCADE;
            DROP TABLE IF EXISTS alembic_version CASCADE;
        """))
        
        # Crear tablas base primero
        connection.execute(text("""
            CREATE TABLE jugadores (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                apellidos VARCHAR(200) NOT NULL,
                club VARCHAR(100),
                activo BOOLEAN DEFAULT TRUE,
                CONSTRAINT uix_nombre_apellidos UNIQUE (nombre, apellidos)
            );

            CREATE TABLE campeonatos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(200) NOT NULL,
                fecha_inicio DATE NOT NULL,
                dias_duracion INTEGER NOT NULL,
                numero_partidas INTEGER NOT NULL,
                pm INTEGER NOT NULL,
                activo BOOLEAN DEFAULT TRUE,
                partida_actual INTEGER DEFAULT 0,
                finalizado BOOLEAN DEFAULT FALSE,
                CONSTRAINT uix_nombre_campeonato UNIQUE (nombre)
            );
        """))
        
        # Luego crear las tablas que dependen de las anteriores
        connection.execute(text("""
            CREATE TABLE jugador_campeonato (
                jugador_id INTEGER REFERENCES jugadores(id),
                campeonato_id INTEGER REFERENCES campeonatos(id),
                PRIMARY KEY (jugador_id, campeonato_id)
            );

            CREATE TABLE pareja_partida (
                id SERIAL PRIMARY KEY,
                jugador1_id INTEGER REFERENCES jugadores(id),
                jugador2_id INTEGER REFERENCES jugadores(id),
                campeonato_id INTEGER REFERENCES campeonatos(id),
                num_partida INTEGER NOT NULL,
                num_mesa INTEGER NOT NULL,
                CONSTRAINT uix_pareja_partida UNIQUE (campeonato_id, num_partida, num_mesa, jugador1_id, jugador2_id)
            );

            CREATE TABLE resultado (
                id SERIAL PRIMARY KEY,
                jugador_id INTEGER REFERENCES jugadores(id),
                campeonato_id INTEGER REFERENCES campeonatos(id),
                num_partida INTEGER NOT NULL,
                num_mesa INTEGER NOT NULL,
                num_pareja INTEGER NOT NULL,
                puntos INTEGER NOT NULL,
                CONSTRAINT uix_resultado UNIQUE (campeonato_id, num_partida, num_mesa, jugador_id)
            );
        """))
        
        connection.commit()