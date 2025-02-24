-- Primero, eliminar las restricciones existentes
ALTER TABLE parejas_partida DROP CONSTRAINT IF EXISTS parejas_partida_jugador1_id_fkey;
ALTER TABLE parejas_partida DROP CONSTRAINT IF EXISTS parejas_partida_jugador2_id_fkey;
ALTER TABLE parejas_partida DROP CONSTRAINT IF EXISTS fk_jugador2_campeonato;
ALTER TABLE parejas_partida DROP CONSTRAINT IF EXISTS uix_jugador1_partida;
ALTER TABLE parejas_partida DROP CONSTRAINT IF EXISTS uix_jugador2_partida;
ALTER TABLE parejas_partida DROP CONSTRAINT IF EXISTS uix_pareja_mesa_partida;

-- Permitir que jugador2_id sea NULL
ALTER TABLE parejas_partida ALTER COLUMN jugador2_id DROP NOT NULL;

-- Agregar las nuevas restricciones
ALTER TABLE parejas_partida ADD CONSTRAINT parejas_partida_jugador1_id_fkey 
    FOREIGN KEY (jugador1_id) REFERENCES jugadores(id);

ALTER TABLE parejas_partida ADD CONSTRAINT parejas_partida_jugador2_id_fkey 
    FOREIGN KEY (jugador2_id) REFERENCES jugadores(id);

ALTER TABLE parejas_partida ADD CONSTRAINT uix_pareja_mesa_partida 
    UNIQUE (partida, mesa, numero_pareja, campeonato_id);

ALTER TABLE parejas_partida ADD CONSTRAINT uix_jugador1_partida 
    UNIQUE (partida, jugador1_id, campeonato_id);

-- Crear un índice único condicional para jugador2_id que solo se aplica cuando no es nulo
CREATE UNIQUE INDEX uix_jugador2_partida 
    ON parejas_partida (partida, jugador2_id, campeonato_id) 
    WHERE jugador2_id IS NOT NULL; 