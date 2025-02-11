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
    id SERIAL PRIMARY KEY,
    nombre VARCHAR NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    campeonato_id INTEGER REFERENCES campeonatos(id)
);

-- Crear tabla resultados
CREATE TABLE resultados (
    id SERIAL PRIMARY KEY,
    jugador_id INTEGER REFERENCES jugadores(id),
    campeonato_id INTEGER REFERENCES campeonatos(id),
    partida INTEGER NOT NULL,
    PT INTEGER NOT NULL DEFAULT 0,
    MG INTEGER NOT NULL DEFAULT 0,
    UNIQUE(jugador_id, campeonato_id, partida)
); 