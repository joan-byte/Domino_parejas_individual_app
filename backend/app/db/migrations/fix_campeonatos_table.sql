-- Eliminar índices y restricciones existentes
DROP INDEX IF EXISTS ix_campeonatos_nombre;
DROP INDEX IF EXISTS idx_campeonatos_nombre;
DROP INDEX IF EXISTS campeonatos_nombre_key;
ALTER TABLE campeonatos DROP CONSTRAINT IF EXISTS uix_nombre_fecha;

-- Recrear la tabla con la estructura correcta
CREATE TABLE IF NOT EXISTS campeonatos_new (
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

-- Copiar datos si la tabla existe
INSERT INTO campeonatos_new 
SELECT id, nombre, fecha_inicio, dias_duracion, numero_partidas, "PM", activo, partida_actual, finalizado 
FROM campeonatos;

-- Eliminar la tabla antigua y renombrar la nueva
DROP TABLE campeonatos CASCADE;
ALTER TABLE campeonatos_new RENAME TO campeonatos;

-- Crear las restricciones necesarias
ALTER TABLE campeonatos 
ADD CONSTRAINT uix_nombre_fecha UNIQUE (nombre, fecha_inicio); 