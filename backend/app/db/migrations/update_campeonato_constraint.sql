-- Eliminar la restricción única anterior si existe
DROP INDEX IF EXISTS ix_campeonatos_nombre;

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