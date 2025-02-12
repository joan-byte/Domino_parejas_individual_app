-- Eliminar el índice único del nombre
DROP INDEX IF EXISTS ix_campeonatos_nombre;

-- Recrear el índice sin la restricción única
CREATE INDEX IF NOT EXISTS idx_campeonatos_nombre ON campeonatos(nombre);

-- Asegurarse de que la restricción única compuesta existe
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uix_nombre_fecha'
    ) THEN
        ALTER TABLE campeonatos
        ADD CONSTRAINT uix_nombre_fecha UNIQUE (nombre, fecha_inicio);
    END IF;
END $$; 