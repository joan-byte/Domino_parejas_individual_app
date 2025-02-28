# Imagen base de Python con soporte multiplataforma
FROM --platform=$BUILDPLATFORM python:3.11-slim as builder

# Crear usuario no root
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependencias y curl para healthcheck
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Etapa final
FROM --platform=$TARGETPLATFORM python:3.11-slim

# Crear usuario no root
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Instalar curl para healthcheck
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar las dependencias y el código desde el builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /app /app

# Establecer permisos correctos
RUN chown -R appuser:appgroup /app

# Cambiar al usuario no root
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 