-- Añadir la columna MG a la tabla resultados
ALTER TABLE resultados ADD COLUMN "MG" INTEGER DEFAULT 0;

-- Actualizar los registros existentes con valor por defecto
UPDATE resultados SET "MG" = 0; 