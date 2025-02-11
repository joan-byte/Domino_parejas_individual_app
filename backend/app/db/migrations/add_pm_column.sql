-- Añadir la columna PM a la tabla campeonatos
ALTER TABLE campeonatos ADD COLUMN "PM" INTEGER DEFAULT 300;

-- Actualizar los registros existentes con valor por defecto
UPDATE campeonatos SET "PM" = 300; 