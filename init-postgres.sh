#!/bin/bash

# En producción, las variables de entorno ya están definidas en el Dockerfile
# No es necesario leer desde archivos de secretos

# Esperar a que los archivos de secrets estén disponibles
while [ ! -f /run/secrets/postgres_user ] || [ ! -f /run/secrets/postgres_password ] || [ ! -f /run/secrets/postgres_db ]; do
    echo "Esperando a que los secrets estén disponibles..."
    sleep 1
done

# Leer los secrets
DB_USER=$(cat /run/secrets/postgres_user)
DB_PASS=$(cat /run/secrets/postgres_password)
DB_NAME=$(cat /run/secrets/postgres_db)

echo "Inicializando PostgreSQL con usuario: $DB_USER, base de datos: $DB_NAME"

# Iniciar PostgreSQL temporalmente para crear usuario y base de datos
/usr/lib/postgresql/15/bin/pg_ctl -D /var/lib/postgresql/data start

# Crear usuario y base de datos
psql --command "CREATE USER $DB_USER WITH SUPERUSER PASSWORD '$DB_PASS';"
createdb -O $DB_USER $DB_NAME

# Verificar que la base de datos se creó correctamente
echo "Verificando la creación de la base de datos..."
psql -l | grep $DB_NAME

# Detener PostgreSQL
/usr/lib/postgresql/15/bin/pg_ctl -D /var/lib/postgresql/data stop

echo "Inicialización de PostgreSQL completada" 