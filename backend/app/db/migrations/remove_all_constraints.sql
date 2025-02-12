-- Desactivar temporalmente las restricciones de clave foránea
SET session_replication_role = 'replica';

-- Eliminar todos los índices y restricciones existentes
DROP INDEX IF EXISTS ix_campeonatos_nombre;
DROP INDEX IF EXISTS idx_campeonatos_nombre;
DROP INDEX IF EXISTS campeonatos_nombre_key;
ALTER TABLE campeonatos DROP CONSTRAINT IF EXISTS uix_nombre_fecha;
ALTER TABLE campeonatos DROP CONSTRAINT IF EXISTS campeonatos_pkey CASCADE;

-- Crear una tabla temporal con la estructura deseada
CREATE TABLE campeonatos_temp (
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

-- Copiar los datos existentes
INSERT INTO campeonatos_temp 
SELECT * FROM campeonatos;

-- Eliminar la tabla original y renombrar la temporal
DROP TABLE campeonatos CASCADE;
ALTER TABLE campeonatos_temp RENAME TO campeonatos;

-- Recrear las claves foráneas
ALTER TABLE jugadores 
ADD CONSTRAINT jugadores_campeonato_id_fkey 
FOREIGN KEY (campeonato_id) REFERENCES campeonatos(id) ON DELETE CASCADE;

ALTER TABLE parejas_partida 
ADD CONSTRAINT parejas_partida_campeonato_id_fkey 
FOREIGN KEY (campeonato_id) REFERENCES campeonatos(id) ON DELETE CASCADE;

ALTER TABLE resultados 
ADD CONSTRAINT resultados_campeonato_id_fkey 
FOREIGN KEY (campeonato_id) REFERENCES campeonatos(id) ON DELETE CASCADE;

-- Reactivar las restricciones de clave foránea
SET session_replication_role = 'origin'; 