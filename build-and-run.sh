#!/bin/bash

# Colores para los mensajes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Configurando builder multi-arquitectura...${NC}"
docker buildx create --name multiarch-builder --driver docker-container --bootstrap || true
docker buildx use multiarch-builder

echo -e "${BLUE}Construyendo imagen para AMD64 y ARM64...${NC}"
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag domino-app:latest \
  --load \
  .

# Detectar la arquitectura del sistema
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
    export TARGETPLATFORM=linux/arm64
else
    export TARGETPLATFORM=linux/amd64
fi

echo -e "${GREEN}Iniciando la aplicación para arquitectura $TARGETPLATFORM...${NC}"
docker compose up 