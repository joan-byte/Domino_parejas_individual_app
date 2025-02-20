-- Verificar si la columna existe con cualquier nombre
DO $$
BEGIN
    -- Si la columna 'pm' existe, renombrarla a 'PM'
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'campeonatos' AND column_name = 'pm') THEN
        ALTER TABLE campeonatos RENAME COLUMN pm TO "PM";
    -- Si la columna no existe, crearla
    ELSIF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'campeonatos' AND column_name = 'PM') THEN
        ALTER TABLE campeonatos ADD COLUMN "PM" INTEGER NOT NULL DEFAULT 300;
    END IF;
END $$;

-- Renombrar las columnas de resultados a mayúsculas
ALTER TABLE resultados RENAME COLUMN pt TO "PT";
ALTER TABLE resultados RENAME COLUMN pv TO "PV";
ALTER TABLE resultados RENAME COLUMN pc TO "PC";
ALTER TABLE resultados RENAME COLUMN pg TO "PG";
ALTER TABLE resultados RENAME COLUMN mg TO "MG"; 