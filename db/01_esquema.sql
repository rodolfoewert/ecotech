PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS persona (
    rut     TEXT PRIMARY KEY,
    nombre  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS departamento (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS proyecto (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT NOT NULL,
    fecha_inicio  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS empleado (
    rut              TEXT PRIMARY KEY,
    fecha_ingreso    TEXT NOT NULL,
    sueldo_base      INTEGER NOT NULL,
    departamento_id  INTEGER,
    FOREIGN KEY (rut) REFERENCES persona(rut) ON DELETE CASCADE,
    FOREIGN KEY (departamento_id) REFERENCES departamento(id)
);

CREATE TABLE IF NOT EXISTS registro_tiempo (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    empleado_rut  TEXT NOT NULL,
    proyecto_id   INTEGER NOT NULL,
    horas         REAL NOT NULL,
    fecha         TEXT NOT NULL,
    FOREIGN KEY (empleado_rut) REFERENCES empleado(rut) ON DELETE CASCADE,
    FOREIGN KEY (proyecto_id) REFERENCES proyecto(id)
);

CREATE TABLE IF NOT EXISTS informe (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo            TEXT NOT NULL,
    fecha_generacion  TEXT NOT NULL,
    proyecto_id       INTEGER,
    FOREIGN KEY (proyecto_id) REFERENCES proyecto(id)
);