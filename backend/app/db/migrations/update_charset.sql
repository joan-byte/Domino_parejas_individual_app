-- Actualizar la codificación de la base de datos
SET client_encoding = 'UTF8';

-- Actualizar la tabla jugadores
ALTER TABLE jugadores
    ALTER COLUMN nombre TYPE VARCHAR(100) COLLATE "es_ES.UTF-8",
    ALTER COLUMN apellidos TYPE VARCHAR(200) COLLATE "es_ES.UTF-8",
    ALTER COLUMN club TYPE VARCHAR(100) COLLATE "es_ES.UTF-8";

-- Actualizar la tabla campeonatos
ALTER TABLE campeonatos
    ALTER COLUMN nombre TYPE VARCHAR(100) COLLATE "es_ES.UTF-8";

-- Verificar que no hay datos corruptos
DO $$
BEGIN
    -- Intentar convertir los datos existentes usando encode/decode
    UPDATE jugadores
    SET nombre = encode(decode(nombre, 'escape'), 'UTF8'),
        apellidos = encode(decode(apellidos, 'escape'), 'UTF8'),
        club = encode(decode(club, 'escape'), 'UTF8')
    WHERE nombre IS NOT NULL OR apellidos IS NOT NULL OR club IS NOT NULL;

    UPDATE campeonatos
    SET nombre = encode(decode(nombre, 'escape'), 'UTF8')
    WHERE nombre IS NOT NULL;
END $$; 