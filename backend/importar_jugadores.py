import json
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.db.base import get_db
from app.models.jugador import Jugador

def importar_jugadores(campeonato_id: int):
    """Importa jugadores desde el archivo jugadores_backup.json al campeonato especificado"""
    try:
        # Obtener sesión de base de datos
        db = next(get_db())
        
        # Leer el archivo de backup
        with open("jugadores_backup.json", "r") as file:
            jugadores_data = json.load(file)
        
        jugadores_importados = []
        nuevo_id = 1  # Inicializar el ID
        
        for jugador_data in jugadores_data:
            try:
                # Crear el nuevo jugador
                nuevo_jugador = Jugador(
                    id=nuevo_id,
                    nombre=jugador_data["nombre"],
                    apellidos=jugador_data["apellidos"],
                    club=jugador_data["club"],
                    activo=True,
                    campeonato_id=campeonato_id
                )
                
                db.add(nuevo_jugador)
                db.commit()  # Commit después de cada jugador
                
                print(f"Importado: {jugador_data['nombre']} {jugador_data['apellidos']} (ID: {nuevo_id})")
                jugadores_importados.append(nuevo_jugador)
                nuevo_id += 1  # Incrementar el ID para el siguiente jugador
                
            except Exception as e:
                db.rollback()
                print(f"Error al importar jugador {jugador_data['nombre']} {jugador_data['apellidos']}: {str(e)}")
                continue
        
        print(f"\nSe importaron {len(jugadores_importados)} jugadores exitosamente")
        
    except FileNotFoundError:
        print("Error: No se encontró el archivo jugadores_backup.json")
    except Exception as e:
        print(f"Error al importar jugadores: {str(e)}")

if __name__ == "__main__":
    # Solicitar el ID del campeonato
    campeonato_id = int(input("Ingrese el ID del nuevo campeonato: "))
    importar_jugadores(campeonato_id) 