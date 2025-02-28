#!/bin/bash

# Función para leer secrets
read_secret() {
    cat "$1" | tr -d '\n'  # Eliminar posibles saltos de línea
}

# Leer credenciales desde secrets y exportarlas como variables de entorno
export DB_PASS=$(read_secret /run/secrets/postgres_password)
export PGPASSWORD=$DB_PASS

# Iniciar Nginx
nginx

# Esperar a que PostgreSQL esté listo
until pg_isready -h postgres -U individual -d domino_parejas_individualdb; do
    echo "Esperando a que PostgreSQL esté listo..."
    sleep 2
done

# Iniciar el backend con las variables de entorno correctas
cd /app && DB_PASS=$DB_PASS uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 