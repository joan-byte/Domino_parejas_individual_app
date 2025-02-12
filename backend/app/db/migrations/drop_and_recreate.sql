-- Eliminar todas las tablas relacionadas en orden
DROP TABLE IF EXISTS resultados CASCADE;
DROP TABLE IF EXISTS jugadores CASCADE;
DROP TABLE IF EXISTS parejas_partida CASCADE;
DROP TABLE IF EXISTS campeonatos CASCADE;

-- Recrear la tabla campeonatos desde cero
CREATE TABLE campeonatos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR NOT NULL,
    fecha_inicio DATE NOT NULL,
    dias_duracion INTEGER NOT NULL,
    numero_partidas INTEGER NOT NULL,
    "PM" INTEGER NOT NULL DEFAULT 300,
    activo BOOLEAN DEFAULT TRUE,
    partida_actual INTEGER DEFAULT 0,
    finalizado BOOLEAN DEFAULT FALSE,
    CONSTRAINT uix_nombre_fecha UNIQUE (nombre, fecha_inicio)
);

-- Recrear las tablas relacionadas
CREATE TABLE jugadores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR NOT NULL,
    apellidos VARCHAR NOT NULL,
    club VARCHAR,
    campeonato_id INTEGER REFERENCES campeonatos(id) ON DELETE CASCADE
);

CREATE TABLE parejas_partida (
    id SERIAL PRIMARY KEY,
    campeonato_id INTEGER REFERENCES campeonatos(id) ON DELETE CASCADE,
    partida INTEGER NOT NULL,
    mesa INTEGER NOT NULL,
    numero_pareja INTEGER NOT NULL,
    jugador1_id INTEGER NOT NULL,
    jugador2_id INTEGER NOT NULL
);

CREATE TABLE resultados (
    id SERIAL PRIMARY KEY,
    campeonato_id INTEGER REFERENCES campeonatos(id) ON DELETE CASCADE,
    partida INTEGER NOT NULL,
    mesa INTEGER NOT NULL,
    jugador INTEGER NOT NULL,
    PT INTEGER NOT NULL DEFAULT 0,
    PV INTEGER NOT NULL DEFAULT 0,
    PC INTEGER NOT NULL DEFAULT 0,
    PG INTEGER NOT NULL DEFAULT 0,
    MG INTEGER NOT NULL DEFAULT 0
); 