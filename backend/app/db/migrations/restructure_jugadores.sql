-- Eliminar las restricciones de clave foránea existentes
ALTER TABLE resultados DROP CONSTRAINT IF EXISTS resultados_jugador_id_campeonato_id_fkey;
ALTER TABLE resultados DROP CONSTRAINT IF EXISTS resultado_jugador_id_fkey;
ALTER TABLE parejas_partida DROP CONSTRAINT IF EXISTS fk_jugador1_campeonato;
ALTER TABLE parejas_partida DROP CONSTRAINT IF EXISTS fk_jugador2_campeonato;
ALTER TABLE parejas_partida DROP CONSTRAINT IF EXISTS parejas_partida_jugador1_id_fkey;
ALTER TABLE parejas_partida DROP CONSTRAINT IF EXISTS parejas_partida_jugador2_id_fkey;

-- Crear tabla temporal para jugadores
CREATE TABLE jugadores_new (
    id INTEGER NOT NULL,
    campeonato_id INTEGER NOT NULL REFERENCES campeonatos(id),
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(200) NOT NULL,
    club VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (id, campeonato_id)
);

-- Migrar datos de jugadores a la nueva estructura
INSERT INTO jugadores_new (id, campeonato_id, nombre, apellidos, club, activo)
SELECT 
    j.id,
    1 as campeonato_id, -- Asumimos que todos los jugadores existentes pertenecen al campeonato 1
    j.nombre,
    j.apellidos,
    j.club,
    j.activo
FROM jugadores j;

-- Eliminar tabla antigua
DROP TABLE jugadores CASCADE;

-- Renombrar tabla temporal
ALTER TABLE jugadores_new RENAME TO jugadores;

-- Recrear las restricciones de clave foránea
ALTER TABLE parejas_partida ADD CONSTRAINT fk_jugador1 
    FOREIGN KEY (jugador1_id, campeonato_id) REFERENCES jugadores(id, campeonato_id);
ALTER TABLE parejas_partida ADD CONSTRAINT fk_jugador2 
    FOREIGN KEY (jugador2_id, campeonato_id) REFERENCES jugadores(id, campeonato_id);
ALTER TABLE resultados ADD CONSTRAINT fk_jugador_resultado 
    FOREIGN KEY (jugador_id, campeonato_id) REFERENCES jugadores(id, campeonato_id); 