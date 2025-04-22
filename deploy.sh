#!/bin/bash

# Script para desplegar la aplicación Domino Parejas Individual
# Autor: Joan Alba
# Fecha: Marzo 2025

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Iniciando despliegue de Domino Parejas Individual ===${NC}"

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker no está instalado. Por favor, instala Docker primero.${NC}"
    exit 1
fi

# Verificar si docker-compose está instalado
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose no está instalado. Por favor, instala Docker Compose primero.${NC}"
    exit 1
fi

# Crear directorio de secretos si no existe
if [ ! -d "./secrets" ]; then
    echo -e "${YELLOW}Creando directorio de secretos...${NC}"
    mkdir -p ./secrets
    
    # Crear archivos de secretos con valores predeterminados
    echo "individual" > ./secrets/postgres_user.txt
    echo "password123" > ./secrets/postgres_password.txt
    echo "domino_db" > ./secrets/postgres_db.txt
    echo "your-secret-key-here" > ./secrets/secret_key.txt
    
    echo -e "${GREEN}Archivos de secretos creados con valores predeterminados.${NC}"
    echo -e "${YELLOW}IMPORTANTE: Considera cambiar estos valores para un entorno de producción.${NC}"
else
    echo -e "${GREEN}Directorio de secretos ya existe.${NC}"
fi

# Descargar la imagen más reciente
echo -e "${YELLOW}Descargando la imagen más reciente de Docker Hub...${NC}"
docker pull joanalba/domino_parejas_individual:latest

# Iniciar los contenedores
echo -e "${YELLOW}Iniciando los contenedores...${NC}"
docker compose up -d

# Verificar si los contenedores están en ejecución
if [ $? -eq 0 ]; then
    echo -e "${GREEN}¡Despliegue completado con éxito!${NC}"
    echo -e "${GREEN}La aplicación está disponible en:${NC}"
    echo -e "${GREEN}- Frontend: http://localhost:80${NC}"
    echo -e "${GREEN}- API Docs: http://localhost:8000/docs${NC}"
else
    echo -e "${RED}Error al iniciar los contenedores. Revisa los logs con 'docker compose logs'.${NC}"
    exit 1
fi

echo -e "${YELLOW}=== Fin del despliegue ===${NC}" 