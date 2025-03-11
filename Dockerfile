# Etapa de construcción del frontend
FROM --platform=$BUILDPLATFORM node:18-alpine as frontend-builder

# Crear usuario no root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /frontend

# Copiar solo los archivos de dependencias primero para mejor uso de caché
COPY frontend/package*.json ./

# Instalación de dependencias del frontend
RUN npm install

# Copia de archivos del frontend y construcción
COPY frontend/ .
RUN npm run build || exit 1

# Etapa final
FROM --platform=$TARGETPLATFORM python:3.11-slim

# Argumentos para multi-arquitectura
ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Crear usuario no root
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Instalación de dependencias del sistema y PostgreSQL
RUN apt-get update && apt-get install -y \
    nginx \
    gcc \
    python3-dev \
    postgresql \
    postgresql-contrib \
    postgresql-client \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Configuración de Nginx
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copia de archivos del frontend construido
COPY --from=frontend-builder /frontend/dist /var/www/html

# Configuración del backend
WORKDIR /app

# Copiar solo requirements.txt primero para mejor uso de caché
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uvicorn[standard]>=0.24.0 pydantic[email]>=2.0.0

COPY backend/ .

# Valores hardcodeados para producción (sin .env ni secrets externos)
ENV DB_HOST=localhost \
    DB_PORT=5432 \
    DB_NAME=dominodb \
    DB_USER=dominouser \
    DB_PASS=individual_password \
    SECRET_KEY=c1c6b8e5f7a3d2e9b8c7a6f5d4e3c2b1a0 \
    POSTGRES_HOST=/var/run/postgresql

# Crear archivo de configuración de base de datos corregido
COPY fix-db-connection.py /app/app/db/base.py

# Script de inicio y supervisord
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Configuración de supervisord
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Crear directorios necesarios
RUN mkdir -p /var/lib/postgresql/data /var/run/postgresql /var/log/supervisor

# Establecer permisos correctos
RUN chown -R postgres:postgres /var/lib/postgresql/data /var/run/postgresql && \
    chmod 2777 /var/run/postgresql && \
    chown -R appuser:appgroup /app /var/www/html /var/log/nginx /var/lib/nginx /run && \
    chown -R root:root /var/log/supervisor

# Script para inicializar PostgreSQL
COPY init-postgres.sh /init-postgres.sh
RUN chmod +x /init-postgres.sh

# Modificar los scripts para usar variables de entorno en lugar de secrets
RUN sed -i 's|read_secret /run/secrets/postgres_user|echo "$DB_USER"|g' /start.sh && \
    sed -i 's|read_secret /run/secrets/postgres_db|echo "$DB_NAME"|g' /start.sh && \
    sed -i 's|read_secret /run/secrets/postgres_password|echo "$DB_PASS"|g' /start.sh && \
    sed -i 's|read_secret /run/secrets/postgres_user|echo "$DB_USER"|g' /init-postgres.sh && \
    sed -i 's|read_secret /run/secrets/postgres_db|echo "$DB_NAME"|g' /init-postgres.sh && \
    sed -i 's|read_secret /run/secrets/postgres_password|echo "$DB_PASS"|g' /init-postgres.sh

EXPOSE 80 8000 5432

# Configuración del healthcheck para verificar que la aplicación está funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Cambiar temporalmente al usuario postgres del sistema para inicializar la BD
USER postgres
RUN /usr/lib/postgresql/15/bin/initdb -D /var/lib/postgresql/data && \
    echo "unix_socket_directories = '/var/run/postgresql'" >> /var/lib/postgresql/data/postgresql.conf && \
    echo "listen_addresses = '*'" >> /var/lib/postgresql/data/postgresql.conf && \
    echo "host all all 0.0.0.0/0 md5" >> /var/lib/postgresql/data/pg_hba.conf && \
    echo "local all all trust" >> /var/lib/postgresql/data/pg_hba.conf

# Volver al usuario root para que supervisord pueda gestionar los servicios
USER root

# Etiquetas para la imagen
LABEL org.opencontainers.image.description="Aplicación Domino Parejas Individual - Multicontenedor (Backend, Frontend, PostgreSQL)"
LABEL org.opencontainers.image.authors="joanalba"
LABEL org.opencontainers.image.version="1.0"
LABEL org.opencontainers.image.architecture="${TARGETPLATFORM}"

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"] 