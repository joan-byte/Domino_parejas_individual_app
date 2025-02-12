-- Eliminar todas las restricciones e índices existentes
DROP INDEX IF EXISTS ix_campeonatos_nombre;
DROP INDEX IF EXISTS idx_campeonatos_nombre;
DROP INDEX IF EXISTS campeonatos_nombre_key;
ALTER TABLE campeonatos DROP CONSTRAINT IF EXISTS uix_nombre_fecha;
ALTER TABLE campeonatos DROP CONSTRAINT IF EXISTS campeonatos_pkey CASCADE;

-- Recrear la tabla desde cero
DROP TABLE IF EXISTS campeonatos_new;
CREATE TABLE campeonatos_new (
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
INSERT INTO campeonatos_new 
SELECT * FROM campeonatos;

-- Eliminar la tabla antigua y renombrar la nueva
DROP TABLE campeonatos CASCADE;
ALTER TABLE campeonatos_new RENAME TO campeonatos;

-- Recrear las relaciones
ALTER TABLE jugadores 
ADD CONSTRAINT jugadores_campeonato_id_fkey 
FOREIGN KEY (campeonato_id) REFERENCES campeonatos(id) ON DELETE CASCADE;

ALTER TABLE parejas_partida 
ADD CONSTRAINT parejas_partida_campeonato_id_fkey 
FOREIGN KEY (campeonato_id) REFERENCES campeonatos(id) ON DELETE CASCADE;

ALTER TABLE resultados 
ADD CONSTRAINT resultados_campeonato_id_fkey 
FOREIGN KEY (campeonato_id) REFERENCES campeonatos(id) ON DELETE CASCADE; 