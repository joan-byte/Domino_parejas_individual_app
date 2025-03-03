# Domino Parejas Individual App

## Requisitos Previos

### Windows
1. **Instalar Docker Desktop**
   - Descargar [Docker Desktop para Windows](https://www.docker.com/products/docker-desktop/)
   - Asegurarse de que WSL2 está instalado y configurado
   - Reiniciar el equipo después de la instalación

### macOS
1. **Instalar Docker Desktop**
   - Para Apple Silicon (M1/M2/M3): Descargar la versión ARM64
   - Para Intel: Descargar la versión AMD64
   - [Descargar Docker Desktop para macOS](https://www.docker.com/products/docker-desktop/)

### Linux
1. **Instalar Docker y Docker Compose**
   ```bash
   # Actualizar el sistema
   sudo apt-get update

   # Instalar dependencias
   sudo apt-get install -y \
       ca-certificates \
       curl \
       gnupg \
       lsb-release

   # Añadir la clave GPG oficial de Docker
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

   # Configurar el repositorio
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

   # Instalar Docker
   sudo apt-get update
   sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

   # Añadir usuario al grupo docker
   sudo usermod -aG docker $USER
   ```

## Preparación de Archivos

1. **Estructura del Directorio**
   ```
   Domino_Individual_Deploy/
   ├── docker-compose.yml
   └── secrets/
       ├── postgres_password.txt
       └── secret_key.txt
   ```

2. **Configuración de Secrets**
   - **postgres_password.txt**: Contraseña para la base de datos PostgreSQL
     ```
     MiContraseñaSegura123
     ```
   - **secret_key.txt**: Clave secreta para la aplicación
     ```
     MiClaveSecretaLarga123!@#
     ```
   
   **Importante**: 
   - Los archivos no deben contener saltos de línea al final
   - Usar contraseñas seguras
   - No compartir estos archivos en repositorios públicos

## Despliegue de la Aplicación

1. **Preparar el Directorio**
   ```bash
   # Crear y acceder al directorio
   mkdir Domino_Individual_Deploy
   cd Domino_Individual_Deploy
   
   # Copiar archivos necesarios
   cp -r /ruta/original/secrets .
   cp /ruta/original/docker-compose.yml .
   ```

2. **Iniciar la Aplicación**
   ```bash
   # Iniciar los servicios
   docker compose up -d
   ```

3. **Verificar el Despliegue**
   - Frontend: http://localhost
     - Debería mostrar la interfaz de usuario del juego
   - Backend API: http://localhost:8000
     - Debería mostrar el mensaje "Bienvenido a la API de Domino Parejas Individual"
   - Documentación API: http://localhost:8000/docs
     - Debería mostrar la documentación Swagger con todos los endpoints disponibles

## Puertos y Servicios

- **Frontend**: Puerto 80
  - Interfaz web accesible en http://localhost
  
- **Backend**: Puerto 8000
  - API REST accesible en http://localhost:8000
  - Documentación Swagger en http://localhost:8000/docs
  
- **Base de Datos**: Puerto 5432 (solo acceso interno)
  - No expuesto al exterior
  - Accesible solo por los servicios internos

## Comandos Útiles

```bash
# Ver logs de los contenedores
docker compose logs -f

# Detener la aplicación
docker compose down

# Reiniciar los servicios
docker compose restart

# Ver estado de los contenedores
docker compose ps

# Limpiar recursos no utilizados
docker system prune -a  # Eliminar todas las imágenes no utilizadas
docker volume prune     # Eliminar volúmenes no utilizados
```

## Mantenimiento y Limpieza

1. **Limpieza de Recursos Temporales**
   ```bash
   # Eliminar contenedores detenidos
   docker container prune

   # Eliminar imágenes no utilizadas
   docker image prune

   # Eliminar volúmenes no utilizados (¡cuidado! esto eliminará datos persistentes)
   docker volume prune
   ```

2. **Actualización de la Aplicación**
   ```bash
   # Detener la aplicación
   docker compose down

   # Eliminar imágenes antiguas
   docker rmi joanalba/domino_parejas_individual:latest

   # Descargar la última versión
   docker compose pull

   # Reiniciar la aplicación
   docker compose up -d
   ```

## Solución de Problemas

1. **Error de permisos en Linux**
   ```bash
   sudo chown -R $USER:$USER .
   ```

2. **Puertos en uso**
   - Verificar que los puertos 80 y 8000 estén disponibles
   - En Linux/macOS: `sudo lsof -i :80,8000`
   - En Windows: `netstat -ano | findstr "80 8000"`

3. **Problemas de conexión**
   - Verificar que Docker Desktop está en ejecución
   - Comprobar los logs: `docker compose logs`
   - Verificar la conectividad: `curl http://localhost:8000`

4. **Problemas con la Base de Datos**
   - Verificar los logs específicos: `docker compose logs postgres`
   - Comprobar el volumen: `docker volume inspect domino_parejas_individual_postgres_data`

## Notas Importantes

- La aplicación está optimizada para arquitecturas ARM64 y AMD64
- Los datos persisten entre reinicios gracias a los volúmenes de Docker
- Se recomienda tener al menos 4GB de RAM libre
- La primera ejecución puede tardar varios minutos mientras se descargan las imágenes
- Los datos de la base de datos se almacenan en un volumen Docker y persisten entre reinicios
- Realizar copias de seguridad periódicas del volumen de la base de datos

## Requisitos Mínimos

- 4GB RAM
- 10GB espacio en disco
- Procesador de 64 bits (AMD64 o ARM64)
- Docker y Docker Compose
- Sistema operativo:
  - Windows 10/11 con WSL2
  - macOS 10.15 o superior
  - Ubuntu 20.04 o superior (u otra distribución Linux compatible)

## Seguridad

- Cambiar las contraseñas por defecto en los archivos de secrets
- No exponer los puertos de la base de datos al exterior
- Mantener Docker y el sistema operativo actualizados
- Realizar copias de seguridad periódicas
- No compartir los archivos de secrets en repositorios públicos
