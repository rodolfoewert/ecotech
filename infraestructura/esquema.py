"""Crea las tablas y actualiza una base anterior sin borrar sus datos."""

from pathlib import Path

from infraestructura.conexion import obtener_conexion


# Las sentencias son constantes del programa, nunca texto ingresado por el usuario.
CAMBIOS = {
    "departamento": ["gerente TEXT NOT NULL DEFAULT ''"],
    "proyecto": ["descripcion TEXT NOT NULL DEFAULT ''"],
    "registro_tiempo": ["descripcion TEXT NOT NULL DEFAULT ''"],
    "empleado": [
        "direccion TEXT NOT NULL DEFAULT ''", "telefono TEXT NOT NULL DEFAULT ''",
        "email TEXT NOT NULL DEFAULT ''", "tipo_contrato TEXT NOT NULL DEFAULT 'planta'",
        "bono REAL NOT NULL DEFAULT 0", "tarifa REAL NOT NULL DEFAULT 0",
    ],
}


def inicializar_bd():
    """Inicializa una base nueva o agrega columnas a la versión usada en clase."""
    ruta = Path(__file__).resolve().parent.parent / "db" / "01_esquema.sql"
    with obtener_conexion() as conn:
        conn.executescript("BEGIN;\n" + ruta.read_text(encoding="utf-8"))
        for tabla, cambios in CAMBIOS.items():
            columnas = {fila[1] for fila in conn.execute(f"PRAGMA table_info({tabla})")}
            for cambio in cambios:
                if cambio.split()[0] not in columnas:
                    conn.execute(f"ALTER TABLE {tabla} ADD COLUMN {cambio}")
        # Los registros antiguos demuestran que ya existía una asignación al proyecto.
        conn.execute("""INSERT OR IGNORE INTO empleado_proyecto (empleado_rut, proyecto_id)
                        SELECT empleado_rut, proyecto_id FROM registro_tiempo""")
