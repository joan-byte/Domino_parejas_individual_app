#!/bin/bash

# En producción, las variables de entorno ya están definidas en el Dockerfile
# No es necesario leer desde archivos de secretos

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