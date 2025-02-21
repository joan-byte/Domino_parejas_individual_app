-- Actualizar la tabla mesas para permitir que pareja_partida2_id sea NULL
ALTER TABLE mesas ALTER COLUMN pareja_partida2_id DROP NOT NULL;

-- Actualizar la tabla resultados para manejar jugadores individuales
ALTER TABLE resultados ALTER COLUMN pareja DROP NOT NULL;
ALTER TABLE resultados ADD COLUMN es_individual BOOLEAN DEFAULT FALSE;

-- Crear índice para optimizar consultas de jugadores individuales
CREATE INDEX idx_resultados_individuales ON resultados(es_individual) WHERE es_individual = TRUE;

-- Actualizar las restricciones de unicidad en parejas_partida para permitir jugadores individuales
ALTER TABLE parejas_partida DROP CONSTRAINT IF EXISTS uix_pareja_mesa_partida;
ALTER TABLE parejas_partida ADD CONSTRAINT uix_pareja_mesa_partida 
    UNIQUE (partida, mesa, numero_pareja, campeonato_id) 
    WHERE numero_pareja = 1 OR (numero_pareja = 2 AND EXISTS (
        SELECT 1 FROM parejas_partida p2 
        WHERE p2.mesa = parejas_partida.mesa 
        AND p2.partida = parejas_partida.partida 
        AND p2.campeonato_id = parejas_partida.campeonato_id 
        AND p2.numero_pareja = 1
    ));

-- Actualizar las restricciones de unicidad para jugadores individuales
ALTER TABLE resultados DROP CONSTRAINT IF EXISTS uix_jugador_mesa_partida;
ALTER TABLE resultados ADD CONSTRAINT uix_jugador_mesa_partida 
    UNIQUE (partida, mesa, jugador, campeonato_id); 