#!/bin/bash

# En producción, las variables de entorno ya están definidas en el Dockerfile
# No es necesario leer desde archivos de secretos

# Esperar a que PostgreSQL esté listo
until pg_isready -h $DB_HOST -U $DB_USER -d $DB_NAME; do
    echo "Esperando a que PostgreSQL esté listo..."
    sleep 2
done

echo "PostgreSQL está listo. Inicializando tablas..."

# Inicializar las tablas en la base de datos
python -c "
from app.db.base import Base, engine
from app.models.jugador import Jugador
from app.models.campeonato import Campeonato
from app.models.resultado import Resultado
from app.models.mesa import Mesa
from app.models.pareja_partida import ParejaPartida
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Crear todas las tablas
    logger.info('Creando tablas en la base de datos...')
    Base.metadata.create_all(bind=engine)
    logger.info('Tablas creadas correctamente')
    
    # Verificar que las tablas se hayan creado
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info(f'Tablas creadas: {tables}')
except Exception as e:
    logger.error(f'Error al crear las tablas: {str(e)}')
"

echo "Iniciando la aplicación..."

# Iniciar el backend con las variables de entorno
cd /app && uvicorn app.main:app --host 0.0.0.0 --port 8000 