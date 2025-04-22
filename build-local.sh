#!/bin/bash

# Colores para los mensajes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con formato
print_message() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Detectar la arquitectura del sistema
ARCH=$(uname -m)
case $ARCH in
    "x86_64")
        PLATFORM="linux/amd64"
        ;;
    "arm64")
        PLATFORM="linux/arm64"
        ;;
    *)
        echo "Arquitectura no soportada: $ARCH"
        exit 1
        ;;
esac

# Establecer las variables de plataforma
export BUILDPLATFORM=$PLATFORM
export TARGETPLATFORM=$PLATFORM

print_message "Verificando archivos de secrets..."
if [ ! -d "secrets" ]; then
    echo "Error: El directorio 'secrets' no existe"
    exit 1
fi

required_secrets=("postgres_user.txt" "postgres_password.txt" "postgres_db.txt" "secret_key.txt")
for secret in "${required_secrets[@]}"; do
    if [ ! -f "secrets/$secret" ]; then
        echo "Error: Falta el archivo de secret 'secrets/$secret'"
        exit 1
    fi
done

print_message "Limpiando contenedores e imágenes anteriores..."
docker stop domino_parejas_individual 2>/dev/null || true
docker rm domino_parejas_individual 2>/dev/null || true
docker rmi domino_parejas_individual:latest 2>/dev/null || true

print_message "Construyendo la imagen multicontenedor para la plataforma $PLATFORM..."

# Construir la imagen
docker build --platform $PLATFORM -t domino_parejas_individual:latest .

if [ $? -eq 0 ]; then
    print_success "Imagen construida exitosamente"
    
    print_message "Iniciando el contenedor..."
    docker run -d \
        --name domino_parejas_individual \
        -p 80:80 \
        -p 8000:8000 \
        -p 5432:5432 \
        --mount type=bind,source="$(pwd)"/secrets/postgres_user.txt,target=/run/secrets/postgres_user,readonly \
        --mount type=bind,source="$(pwd)"/secrets/postgres_password.txt,target=/run/secrets/postgres_password,readonly \
        --mount type=bind,source="$(pwd)"/secrets/postgres_db.txt,target=/run/secrets/postgres_db,readonly \
        --mount type=bind,source="$(pwd)"/secrets/secret_key.txt,target=/run/secrets/secret_key,readonly \
        domino_parejas_individual:latest
    
    if [ $? -eq 0 ]; then
        print_success "Contenedor iniciado exitosamente"
        print_message "Puedes acceder a:"
        echo "- Frontend: http://localhost:80"
        echo "- Backend API docs: http://localhost:8000/docs"
        echo "- Base de datos: localhost:5432"
        
        print_message "Verificando el estado del contenedor..."
        sleep 10
        docker ps
    else
        echo "Error al iniciar el contenedor"
        exit 1
    fi
else
    echo "Error al construir la imagen"
    exit 1
fi 