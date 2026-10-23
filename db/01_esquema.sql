PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS persona (
    rut     TEXT PRIMARY KEY,
    nombre  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS departamento (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre  TEXT NOT NULL,
    gerente TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS proyecto (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT NOT NULL,
    fecha_inicio  DATE NOT NULL,
    descripcion TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS empleado (
    rut              TEXT PRIMARY KEY,
    fecha_ingreso    DATE NOT NULL,
    sueldo_base      REAL NOT NULL CHECK (sueldo_base > 0),
    direccion        TEXT NOT NULL DEFAULT '',
    telefono         TEXT NOT NULL DEFAULT '',
    email            TEXT NOT NULL DEFAULT '',
    tipo_contrato    TEXT NOT NULL DEFAULT 'planta'
                     CHECK (tipo_contrato IN ('planta', 'contratista')),
    bono             REAL NOT NULL DEFAULT 0 CHECK (bono >= 0),
    tarifa           REAL NOT NULL DEFAULT 0 CHECK (tarifa >= 0),
    departamento_id  INTEGER,
    FOREIGN KEY (rut) REFERENCES persona(rut) ON DELETE CASCADE,
    FOREIGN KEY (departamento_id) REFERENCES departamento(id)
);

CREATE TABLE IF NOT EXISTS registro_tiempo (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    empleado_rut  TEXT NOT NULL,
    proyecto_id   INTEGER NOT NULL,
    horas         REAL NOT NULL CHECK (horas > 0 AND horas <= 24),
    fecha         DATE NOT NULL,
    descripcion   TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (empleado_rut) REFERENCES empleado(rut) ON DELETE CASCADE,
    FOREIGN KEY (proyecto_id) REFERENCES proyecto(id)
);

CREATE TABLE IF NOT EXISTS informe (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo            TEXT NOT NULL,
    fecha_generacion  DATE NOT NULL,
    proyecto_id       INTEGER,
    FOREIGN KEY (proyecto_id) REFERENCES proyecto(id)
);
-- La asignación existe aunque el empleado todavía no haya registrado horas.
CREATE TABLE IF NOT EXISTS empleado_proyecto (
    empleado_rut TEXT NOT NULL,
    proyecto_id INTEGER NOT NULL,
    PRIMARY KEY (empleado_rut, proyecto_id),
    FOREIGN KEY (empleado_rut) REFERENCES empleado(rut) ON DELETE CASCADE,
    FOREIGN KEY (proyecto_id) REFERENCES proyecto(id) ON DELETE CASCADE
);
