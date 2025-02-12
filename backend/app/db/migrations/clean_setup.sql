-- Desconectar todas las conexiones activas
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'domino'
AND pid <> pg_backend_pid();

-- Eliminar y recrear la base de datos
DROP DATABASE IF EXISTS domino;
CREATE DATABASE domino;

\c domino;

-- Crear las tablas desde cero
CREATE TABLE campeonatos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR,
    fecha_inicio DATE,
    dias_duracion INTEGER,
    numero_partidas INTEGER,
    "PM" INTEGER DEFAULT 300,
    activo BOOLEAN DEFAULT TRUE,
    partida_actual INTEGER DEFAULT 0,
    finalizado BOOLEAN DEFAULT FALSE
);

CREATE TABLE jugadores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR,
    apellidos VARCHAR,
    club VARCHAR,
    campeonato_id INTEGER REFERENCES campeonatos(id) ON DELETE CASCADE
);

CREATE TABLE parejas_partida (
    id SERIAL PRIMARY KEY,
    campeonato_id INTEGER REFERENCES campeonatos(id) ON DELETE CASCADE,
    partida INTEGER,
    mesa INTEGER,
    numero_pareja INTEGER,
    jugador1_id INTEGER,
    jugador2_id INTEGER
);

CREATE TABLE resultados (
    id SERIAL PRIMARY KEY,
    campeonato_id INTEGER REFERENCES campeonatos(id) ON DELETE CASCADE,
    partida INTEGER,
    mesa INTEGER,
    jugador INTEGER,
    PT INTEGER DEFAULT 0,
    PV INTEGER DEFAULT 0,
    PC INTEGER DEFAULT 0,
    PG INTEGER DEFAULT 0,
    MG INTEGER DEFAULT 0
); 