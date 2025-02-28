# Etapa de construcción
FROM --platform=$BUILDPLATFORM node:18-alpine as build

# Crear usuario no root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Establecer directorio de trabajo
WORKDIR /app

# Copiar package.json y package-lock.json primero para mejor uso de caché
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el código fuente
COPY . .

# Establecer permisos
RUN chown -R appuser:appgroup /app

# Cambiar al usuario no root para la construcción
USER appuser

# Construir la aplicación
RUN npm run build

# Etapa de producción
FROM --platform=$TARGETPLATFORM nginx:alpine

# Crear usuario no root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copiar la configuración de nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar los archivos construidos
COPY --from=build /app/dist /usr/share/nginx/html

# Configurar permisos
RUN chown -R appuser:appgroup /var/cache/nginx /var/log/nginx /etc/nginx/conf.d \
    && touch /var/run/nginx.pid \
    && chown -R appuser:appgroup /var/run/nginx.pid \
    && chmod -R 755 /usr/share/nginx/html

# Cambiar al usuario no root
USER appuser

# Exponer el puerto
EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost:80/ || exit 1

# Iniciar nginx
CMD ["nginx", "-g", "daemon off;"] 