#!/bin/bash

# Script simplificado para construir, ejecutar e inicializar imagen Docker multicontenedor
# - Multicontenedor (backend, frontend, PostgreSQL)
# - Compatible con ARM y AMD
# - Para producción (sin venv)
# - Con secretos

# Nombre de la imagen y tag
IMAGE_NAME="domino_parejas_individual"
TAG="latest"

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para inicializar las tablas de la base de datos
initialize_db() {
    echo -e "${YELLOW}=== INICIALIZANDO TABLAS EN LA BASE DE DATOS ===${NC}"
    
    # Verificar si el contenedor está en ejecución
    if ! docker ps | grep -q $IMAGE_NAME; then
        echo -e "${RED}El contenedor $IMAGE_NAME no está en ejecución.${NC}"
        return 1
    fi
    
    # Ejecutar el comando para inicializar las tablas
    echo -e "${YELLOW}Ejecutando comando para inicializar las tablas...${NC}"
    docker exec -it $IMAGE_NAME python -c "
from app.db.base import Base, engine
from app.models.jugador import Jugador
from app.models.campeonato import Campeonato
from app.models.resultado import Resultado
from app.models.mesa import Mesa
from app.models.pareja_partida import ParejaPartida
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Crear todas las tablas
    logger.info('Creando tablas en la base de datos...')
    Base.metadata.create_all(bind=engine)
    logger.info('Tablas creadas correctamente')
    
    # Verificar que las tablas se hayan creado
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info(f'Tablas creadas: {tables}')
except Exception as e:
    logger.error(f'Error al crear las tablas: {str(e)}')
    raise
"
    
    # Verificar si la ejecución fue exitosa
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Tablas inicializadas correctamente.${NC}"
        return 0
    else
        echo -e "${RED}Error al inicializar las tablas.${NC}"
        return 1
    fi
}

# Mostrar menú de opciones
show_menu() {
    echo -e "${YELLOW}=== DOMINO PAREJAS INDIVIDUAL - DOCKER ===${NC}"
    echo -e "${YELLOW}Selecciona una opción:${NC}"
    echo "1. Construir imagen"
    echo "2. Ejecutar contenedor"
    echo "3. Inicializar base de datos"
    echo "4. Construir y ejecutar (todo en uno)"
    echo "5. Salir"
    read -p "Opción: " option
    
    case $option in
        1)
            build_image
            show_menu
            ;;
        2)
            run_container
            show_menu
            ;;
        3)
            initialize_db
            show_menu
            ;;
        4)
            build_and_run
            ;;
        5)
            echo -e "${GREEN}¡Hasta luego!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Opción inválida.${NC}"
            show_menu
            ;;
    esac
}

# Función para construir la imagen
build_image() {
    echo -e "${YELLOW}=== CONSTRUYENDO IMAGEN MULTICONTENEDOR ===${NC}"
    echo -e "${YELLOW}Imagen: $IMAGE_NAME:$TAG${NC}"
    echo -e "${YELLOW}Contenido: Backend + Frontend + PostgreSQL${NC}"
    
    # Detectar la arquitectura del sistema
    ARCH=$(uname -m)
    if [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
        PLATFORM="linux/arm64"
        echo -e "${BLUE}Arquitectura detectada: ARM64${NC}"
    else
        PLATFORM="linux/amd64"
        echo -e "${BLUE}Arquitectura detectada: AMD64${NC}"
    fi
    
    # Asegurarse de que buildx está disponible
    if ! docker buildx version > /dev/null 2>&1; then
        echo -e "${RED}Error: Docker buildx no está disponible. Por favor, asegúrate de tener Docker 19.03 o superior.${NC}"
        return 1
    fi
    
    # Crear un nuevo builder si no existe
    if ! docker buildx inspect multiarch-builder > /dev/null 2>&1; then
        echo -e "${YELLOW}Creando nuevo builder para multi-arquitectura...${NC}"
        docker buildx create --name multiarch-builder --use
    fi
    
    # Usar el builder
    docker buildx use multiarch-builder
    
    # Iniciar el builder
    docker buildx inspect --bootstrap
    
    # Construir la imagen para la arquitectura local
    echo -e "${YELLOW}Construyendo imagen multicontenedor para $PLATFORM...${NC}"
    docker buildx build --platform $PLATFORM \
        --tag $IMAGE_NAME:$TAG \
        --load \
        .
    
    # Verificar si la construcción fue exitosa
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}¡Construcción exitosa! La imagen $IMAGE_NAME:$TAG está disponible localmente.${NC}"
        return 0
    else
        echo -e "${RED}Error durante la construcción de la imagen.${NC}"
        return 1
    fi
}

# Función para ejecutar el contenedor
run_container() {
    # Detener y eliminar el contenedor si ya existe
    if docker ps -a | grep -q $IMAGE_NAME; then
        echo -e "${YELLOW}Deteniendo y eliminando contenedor existente...${NC}"
        docker stop $IMAGE_NAME >/dev/null 2>&1
        docker rm $IMAGE_NAME >/dev/null 2>&1
    fi
    
    echo -e "${GREEN}Iniciando contenedor multicontenedor...${NC}"
    docker run -d -p 80:80 -p 8000:8000 --name $IMAGE_NAME $IMAGE_NAME:$TAG
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Contenedor iniciado. Puedes acceder a:${NC}"
        echo -e "- Frontend: ${BLUE}http://localhost${NC}"
        echo -e "- Backend API: ${BLUE}http://localhost:8000${NC}"
        echo -e "- Documentación API: ${BLUE}http://localhost:8000/docs${NC}"
        
        # Preguntar si desea ver los logs
        read -p "¿Deseas ver los logs del contenedor? (s/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            docker logs -f $IMAGE_NAME
        fi
        
        return 0
    else
        echo -e "${RED}Error al iniciar el contenedor.${NC}"
        return 1
    fi
}

# Función para construir y ejecutar
build_and_run() {
    build_image
    if [ $? -eq 0 ]; then
        run_container
        if [ $? -eq 0 ]; then
            # Preguntar si desea inicializar la base de datos
            read -p "¿Deseas inicializar la base de datos? (s/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Ss]$ ]]; then
                initialize_db
            fi
        fi
    fi
    
    show_menu
}

# Mostrar el menú principal
show_menu 