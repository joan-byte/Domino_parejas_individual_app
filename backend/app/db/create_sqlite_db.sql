-- Crear tabla campeonatos
CREATE TABLE IF NOT EXISTS campeonatos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    fecha_inicio DATE NOT NULL,
    dias_duracion INTEGER NOT NULL,
    numero_partidas INTEGER NOT NULL,
    PM INTEGER NOT NULL DEFAULT 300,
    activo BOOLEAN DEFAULT 1,
    partida_actual INTEGER DEFAULT 0,
    finalizado BOOLEAN DEFAULT 0
);

-- Crear tabla jugadores
CREATE TABLE IF NOT EXISTS jugadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    club TEXT,
    activo BOOLEAN DEFAULT 1,
    campeonato_id INTEGER,
    FOREIGN KEY (campeonato_id) REFERENCES campeonatos(id) ON DELETE CASCADE
);

-- Crear tabla parejas_partida
CREATE TABLE IF NOT EXISTS parejas_partida (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    partida INTEGER NOT NULL,
    mesa INTEGER NOT NULL,
    jugador1_id INTEGER NOT NULL,
    jugador2_id INTEGER NOT NULL,
    numero_pareja INTEGER NOT NULL,
    campeonato_id INTEGER,
    FOREIGN KEY (campeonato_id) REFERENCES campeonatos(id) ON DELETE CASCADE,
    FOREIGN KEY (jugador1_id) REFERENCES jugadores(id),
    FOREIGN KEY (jugador2_id) REFERENCES jugadores(id),
    UNIQUE (partida, mesa, numero_pareja, campeonato_id),
    UNIQUE (partida, jugador1_id, campeonato_id),
    UNIQUE (partida, jugador2_id, campeonato_id)
);

-- Crear tabla resultados
CREATE TABLE IF NOT EXISTS resultados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    partida INTEGER NOT NULL,
    mesa INTEGER NOT NULL,
    jugador_id INTEGER NOT NULL,
    campeonato_id INTEGER NOT NULL,
    puntos_ganados INTEGER NOT NULL DEFAULT 0,
    puntos_contra INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (jugador_id) REFERENCES jugadores(id),
    FOREIGN KEY (campeonato_id) REFERENCES campeonatos(id) ON DELETE CASCADE,
    UNIQUE (campeonato_id, partida, mesa, jugador_id)
); 