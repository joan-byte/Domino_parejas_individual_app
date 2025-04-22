#!/bin/bash

# En producción, las variables de entorno ya están definidas en el Dockerfile
# No es necesario leer desde archivos de secretos

# Esperar a que los archivos de secrets estén disponibles
while [ ! -f /app/secrets/postgres_user.txt ] || [ ! -f /app/secrets/postgres_password.txt ] || [ ! -f /app/secrets/postgres_db.txt ]; do
    echo "Esperando a que los secrets estén disponibles..."
    sleep 1
done

# Verificar permisos de los secrets
ls -l /app/secrets/
echo "Verificando permisos de secrets..."

# Leer los secrets
DB_USER=$(cat /app/secrets/postgres_user.txt)
DB_PASS=$(cat /app/secrets/postgres_password.txt)
DB_NAME=$(cat /app/secrets/postgres_db.txt)

echo "Inicializando PostgreSQL con usuario: $DB_USER, base de datos: $DB_NAME"

# Esperar a que PostgreSQL esté listo
until pg_isready -h localhost -p 5432; do
    echo "Esperando a que PostgreSQL esté listo..."
    sleep 1
done

# Crear usuario y base de datos con codificación UTF-8
echo "Creando usuario y base de datos con codificación UTF-8..."
psql -h localhost -p 5432 -v ON_ERROR_STOP=1 --username postgres <<-EOSQL
    CREATE USER $DB_USER WITH SUPERUSER PASSWORD '$DB_PASS';
    CREATE DATABASE $DB_NAME OWNER $DB_USER ENCODING 'UTF8' LC_COLLATE='es_ES.UTF-8' LC_CTYPE='es_ES.UTF-8' TEMPLATE=template0;
EOSQL

# Verificar que la base de datos se creó correctamente
echo "Verificando la creación de la base de datos..."
psql -h localhost -p 5432 -l | grep $DB_NAME

echo "Inicialización de PostgreSQL completada" 