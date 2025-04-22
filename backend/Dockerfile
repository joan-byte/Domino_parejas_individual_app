# Imagen base de Python con soporte multiplataforma
FROM --platform=$BUILDPLATFORM python:3.11

# Argumentos para multi-arquitectura
ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Crear usuario no root
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Establecer directorio de trabajo
WORKDIR /app

# Instalar curl para healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt primero para mejor uso de caché
COPY requirements.txt .

# Instalar dependencias con optimizaciones para producción
RUN pip install --no-cache-dir --compile --no-deps -r requirements.txt && \
    pip install --no-cache-dir --compile --no-deps uvicorn[standard]>=0.24.0 pydantic[email]>=2.0.0 && \
    find /usr/local/lib/python3.11 -name '__pycache__' -exec rm -r {} + && \
    find /usr/local/lib/python3.11 -name '*.pyc' -exec rm -f {} +

# Copiar el resto del código
COPY . .

# Eliminar archivos innecesarios para producción
RUN rm -rf \
    tests/ \
    __pycache__/ \
    *.pyc \
    .pytest_cache/ \
    .coverage \
    htmlcov/ \
    .git/ \
    .gitignore \
    README.md \
    requirements-dev.txt \
    venv/ \
    .env.example

# Establecer variables de entorno para producción
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONOPTIMIZE=2

# Cambiar al usuario no root
USER appuser

# Exponer el puerto
EXPOSE 8000

# Healthcheck para verificar que la aplicación está funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Comando para ejecutar la aplicación con optimizaciones
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--proxy-headers", "--forwarded-allow-ips", "*"] 