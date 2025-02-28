# Etapa de construcción del frontend
FROM node:18-alpine as frontend-builder

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
FROM python:3.11-slim

# Crear usuario no root
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Instalación de dependencias del sistema
RUN apt-get update && apt-get install -y \
    nginx \
    gcc \
    python3-dev \
    postgresql-client \
    curl \
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

# Script de inicio
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Establecer permisos correctos
RUN chown -R appuser:appgroup /app /var/www/html /var/log/nginx /var/lib/nginx /run

# Cambiar al usuario no root
USER appuser

EXPOSE 80 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

CMD ["/start.sh"] 