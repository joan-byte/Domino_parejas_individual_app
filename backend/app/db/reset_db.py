from app.db.base import Base, engine

def reset_database():
    # Eliminar todas las tablas
    Base.metadata.drop_all(bind=engine)
    # Crear todas las tablas de nuevo
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Reiniciando la base de datos...")
    reset_database()
    print("¡Base de datos reiniciada exitosamente!")