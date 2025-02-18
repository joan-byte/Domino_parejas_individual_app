import os
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def apply_migrations():
    # Obtener las credenciales de la base de datos desde las variables de entorno
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASS = os.getenv('DB_PASS')

    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        
        # Crear un cursor
        cur = conn.cursor()
        
        print("Aplicando migraciones...")
        
        # Primero ejecutar create_tables.sql si no existe la estructura
        print("1. Creando tablas si no existen...")
        with open('backend/app/db/migrations/create_tables.sql', 'r') as file:
            create_tables_sql = file.read()
            cur.execute(create_tables_sql)
        
        # Luego ejecutar update_charset.sql
        print("2. Actualizando charset...")
        with open('backend/app/db/migrations/update_charset.sql', 'r') as file:
            charset_sql = file.read()
            cur.execute(charset_sql)
        
        # Confirmar los cambios
        conn.commit()
        print("Migraciones completadas exitosamente")
        
    except Exception as e:
        print(f"Error al aplicar la migración: {str(e)}")
        conn.rollback()
    finally:
        # Cerrar la conexión
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    apply_migrations() 