-- Añadir la columna pareja a la tabla resultados
ALTER TABLE resultados ADD COLUMN pareja INTEGER NOT NULL DEFAULT 1;

-- Actualizar los valores de pareja basados en el número de jugador
UPDATE resultados 
SET pareja = CASE 
    WHEN jugador IN (1, 2) THEN 1 
    WHEN jugador IN (3, 4) THEN 2 
    ELSE 1 
END; 