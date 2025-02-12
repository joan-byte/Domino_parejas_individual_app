-- Guardar los datos existentes en una tabla temporal
CREATE TEMP TABLE temp_campeonatos AS SELECT * FROM campeonatos;

-- Eliminar la tabla existente
DROP TABLE IF EXISTS campeonatos CASCADE;

-- Recrear la tabla con la estructura correcta
CREATE TABLE campeonatos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR NOT NULL,
    fecha_inicio DATE NOT NULL,
    dias_duracion INTEGER NOT NULL,
    numero_partidas INTEGER NOT NULL,
    "PM" INTEGER NOT NULL DEFAULT 300,
    activo BOOLEAN DEFAULT TRUE,
    partida_actual INTEGER DEFAULT 0,
    finalizado BOOLEAN DEFAULT FALSE
);

-- Crear la restricción única compuesta
ALTER TABLE campeonatos 
ADD CONSTRAINT uix_nombre_fecha UNIQUE (nombre, fecha_inicio);

-- Crear el índice no único para el nombre
CREATE INDEX idx_campeonatos_nombre ON campeonatos(nombre);

-- Restaurar los datos
INSERT INTO campeonatos 
SELECT * FROM temp_campeonatos;

-- Limpiar
DROP TABLE temp_campeonatos; 