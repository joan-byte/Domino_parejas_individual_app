import os
from sqlalchemy import text
from app.db.base import engine

def run_migration():
    # Leer el archivo SQL
    migration_path = os.path.join(os.path.dirname(__file__), 'migrations', 'add_mg_column.sql')
    
    try:
        with open(migration_path, 'r') as file:
            sql = file.read()
            
        # Ejecutar la migración
        with engine.connect() as connection:
            print("Ejecutando migración...")
            connection.execute(text(sql))
            connection.commit()
            print("¡Migración completada exitosamente!")
            
    except Exception as e:
        print(f"Error durante la migración: {str(e)}")
        raise

if __name__ == "__main__":
    run_migration() 