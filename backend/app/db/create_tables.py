from app.db.base import Base, engine
from app.models import campeonato, jugador, mesa, pareja_partida, resultado

def create_tables():
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Creando tablas en la base de datos...")
    create_tables()
    print("¡Tablas creadas exitosamente!")
    