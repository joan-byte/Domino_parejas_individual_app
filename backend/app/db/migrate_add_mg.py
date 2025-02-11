from app.db.base import Base, engine
import os
from sqlalchemy import text

def migrate_add_mg():
    # Obtener el path de la base de datos
    db_path = "app.db"  # El archivo de base de datos SQLite
    
    # Hacer backup de la base de datos actual
    if os.path.exists(db_path):
        backup_path = "app.db.backup"
        print(f"Haciendo backup de la base de datos a {backup_path}")
        os.rename(db_path, backup_path)
    
    print("Creando nueva base de datos con el campo MG...")
    # Crear todas las tablas nuevamente
    Base.metadata.create_all(bind=engine)
    print("¡Base de datos actualizada exitosamente!")
    
    # Informar al usuario
    print("\nIMPORTANTE: Se ha creado una nueva base de datos con la estructura actualizada.")
    print("La base de datos anterior se ha guardado como 'app.db.backup'")
    print("Los datos deberán ser reintroducidos en la nueva base de datos.")

if __name__ == "__main__":
    migrate_add_mg() 