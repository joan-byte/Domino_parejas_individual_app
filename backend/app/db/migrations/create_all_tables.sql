-- Crear tabla campeonatos
CREATE TABLE IF NOT EXISTS campeonatos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    fecha_inicio DATE NOT NULL,
    dias_duracion INTEGER NOT NULL,
    numero_partidas INTEGER NOT NULL,
    "PM" INTEGER NOT NULL DEFAULT 300,
    activo BOOLEAN DEFAULT TRUE,
    partida_actual INTEGER DEFAULT 0,
    finalizado BOOLEAN DEFAULT FALSE,
    CONSTRAINT uix_nombre_fecha UNIQUE (nombre, fecha_inicio)
);

-- Crear tabla jugadores
DROP TABLE IF EXISTS jugadores CASCADE;
CREATE TABLE IF NOT EXISTS jugadores (
    id INTEGER NOT NULL,
    campeonato_id INTEGER NOT NULL REFERENCES campeonatos(id),
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(200) NOT NULL,
    club VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (id, campeonato_id)
);

-- Crear tabla parejas_partida
CREATE TABLE IF NOT EXISTS parejas_partida (
    id SERIAL PRIMARY KEY,
    partida INTEGER NOT NULL,
    mesa INTEGER NOT NULL,
    jugador1_id INTEGER NOT NULL,
    jugador2_id INTEGER NOT NULL,
    numero_pareja INTEGER NOT NULL,
    campeonato_id INTEGER REFERENCES campeonatos(id),
    CONSTRAINT uix_pareja_mesa_partida UNIQUE (partida, mesa, numero_pareja, campeonato_id),
    CONSTRAINT uix_jugador1_partida UNIQUE (partida, jugador1_id, campeonato_id),
    CONSTRAINT uix_jugador2_partida UNIQUE (partida, jugador2_id, campeonato_id),
    FOREIGN KEY (jugador1_id, campeonato_id) REFERENCES jugadores(id, campeonato_id),
    FOREIGN KEY (jugador2_id, campeonato_id) REFERENCES jugadores(id, campeonato_id)
);

-- Crear tabla resultados
CREATE TABLE IF NOT EXISTS resultados (
    id SERIAL PRIMARY KEY,
    partida INTEGER NOT NULL,
    mesa INTEGER NOT NULL,
    jugador INTEGER NOT NULL,
    jugador_id INTEGER NOT NULL,
    campeonato_id INTEGER NOT NULL,
    pareja INTEGER NOT NULL DEFAULT 1,
    "PT" INTEGER NOT NULL DEFAULT 0,
    "PV" INTEGER NOT NULL DEFAULT 0,
    "PC" INTEGER NOT NULL DEFAULT 0,
    "PG" INTEGER NOT NULL DEFAULT 0,
    "MG" INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (jugador_id, campeonato_id) REFERENCES jugadores(id, campeonato_id)
); 