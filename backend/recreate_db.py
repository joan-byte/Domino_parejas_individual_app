from app.db.base import recreate_database

if __name__ == "__main__":
    print("Recreando la base de datos...")
    recreate_database()
    print("Base de datos recreada exitosamente.") 