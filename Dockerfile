# Usamos una imagen base con Python y Node.js
FROM ubuntu:22.04

# Configurar variables de entorno para evitar interacciones durante la instalación
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Madrid
ENV LANG=es_ES.UTF-8
ENV LANGUAGE=es_ES:es
ENV LC_ALL=es_ES.UTF-8

# Variables de entorno para PostgreSQL
ENV PGDATA=/var/lib/postgresql/data

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    python3.10 \
    python3-pip \
    postgresql-14 \
    postgresql-client-14 \
    nginx \
    supervisor \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Configurar locale
RUN locale-gen es_ES.UTF-8

# Instalar Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Configurar PostgreSQL para aceptar conexiones y usar UTF-8
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/14/main/pg_hba.conf && \
    echo "listen_addresses='*'" >> /etc/postgresql/14/main/postgresql.conf && \
    echo "client_encoding = 'UTF8'" >> /etc/postgresql/14/main/postgresql.conf && \
    echo "default_text_search_config = 'pg_catalog.spanish'" >> /etc/postgresql/14/main/postgresql.conf

# Crear directorios necesarios y establecer permisos
RUN mkdir -p /var/lib/postgresql/data /var/run/postgresql /var/log/supervisor /app/secrets && \
    chown -R postgres:postgres /var/lib/postgresql/data /var/run/postgresql /app/secrets

# Inicializar la base de datos de PostgreSQL con la configuración correcta
USER postgres
RUN /usr/lib/postgresql/14/bin/initdb -D /var/lib/postgresql/data --locale=es_ES.UTF-8
USER root

# Configurar el backend
WORKDIR /app/backend
COPY ./backend/requirements.txt .
RUN pip3 install -r requirements.txt
COPY ./backend .

# Configurar el frontend
WORKDIR /app/frontend
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend .
RUN npm run build

# Copiar archivos de configuración
COPY init-postgres.sh /init-postgres.sh
RUN chmod +x /init-postgres.sh \
    && chown postgres:postgres /init-postgres.sh

COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN rm /etc/nginx/sites-enabled/default

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Exponer puertos
EXPOSE 80 8000 5432

# Establecer PYTHONPATH
ENV PYTHONPATH=/app/backend

# Comando para iniciar todos los servicios
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"] 