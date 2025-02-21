from sqlalchemy import create_engine, text
from app.db.base import Base
from app.models import campeonato, jugador, mesa, pareja_partida, resultado
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://individual:375CheyTac@localhost:5432/domino_parejas_individualdb")

def recreate_database():
    # Crear el motor de la base de datos
    engine = create_engine(DATABASE_URL)
    
    # Crear una conexión
    with engine.connect() as connection:
        # Eliminar las tablas en orden inverso a las dependencias
        connection.execute(text("DROP TABLE IF EXISTS resultados CASCADE"))
        connection.execute(text("DROP TABLE IF EXISTS resultado CASCADE"))
        connection.execute(text("DROP TABLE IF EXISTS mesas CASCADE"))
        connection.execute(text("DROP TABLE IF EXISTS parejas_partida CASCADE"))
        connection.execute(text("DROP TABLE IF EXISTS pareja_partida CASCADE"))
        connection.execute(text("DROP TABLE IF EXISTS jugadores CASCADE"))
        connection.execute(text("DROP TABLE IF EXISTS campeonatos CASCADE"))
        
        # Confirmar los cambios
        connection.commit()
    
    # Crear todas las tablas nuevamente
    Base.metadata.create_all(bind=engine)
    
    print("Base de datos recreada exitosamente")

if __name__ == "__main__":
    recreate_database() 