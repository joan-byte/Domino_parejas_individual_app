-- Asegurar que la base de datos use UTF-8
SET client_encoding = 'UTF8';

-- Crear tabla campeonatos
CREATE TABLE campeonatos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR NOT NULL UNIQUE,
    fecha_inicio DATE NOT NULL,
    dias_duracion INTEGER NOT NULL,
    numero_partidas INTEGER NOT NULL,
    "PM" INTEGER NOT NULL DEFAULT 300,
    activo BOOLEAN DEFAULT TRUE,
    partida_actual INTEGER DEFAULT 0,
    finalizado BOOLEAN DEFAULT FALSE
);

-- Crear tabla jugadores
CREATE TABLE jugadores (
    id INTEGER,
    nombre VARCHAR(100) COLLATE "es_ES.UTF-8",
    apellidos VARCHAR(200) COLLATE "es_ES.UTF-8",
    club VARCHAR(100) COLLATE "es_ES.UTF-8",
    activo BOOLEAN DEFAULT true,
    campeonato_id INTEGER REFERENCES campeonatos(id),
    PRIMARY KEY (id, campeonato_id)
);

-- Crear tabla resultados
CREATE TABLE resultados (
    id SERIAL PRIMARY KEY,
    partida INTEGER NOT NULL,
    mesa INTEGER NOT NULL,
    jugador INTEGER NOT NULL,
    jugador_id INTEGER,
    campeonato_id INTEGER,
    PT INTEGER NOT NULL DEFAULT 0,
    PV INTEGER NOT NULL DEFAULT 0,
    PC INTEGER NOT NULL DEFAULT 0,
    PG INTEGER NOT NULL DEFAULT 0,
    MG INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (jugador_id, campeonato_id) REFERENCES jugadores(id, campeonato_id)
); 