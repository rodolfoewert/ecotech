from pathlib import Path

from infraestructura.conexion import obtener_conexion
from seguridad.cifrado import cifrar, descifrar


# Estas definiciones son fijas; no provienen del usuario.
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
            columnas = []
            for fila in conn.execute(f"PRAGMA table_info({tabla})"):
                columnas.append(fila[1])
            for cambio in cambios:
                if cambio.split()[0] not in columnas:
                    conn.execute(f"ALTER TABLE {tabla} ADD COLUMN {cambio}")
        conn.execute("""INSERT OR IGNORE INTO empleado_proyecto (empleado_rut, proyecto_id)
                        SELECT empleado_rut, proyecto_id FROM registro_tiempo""")
        contactos = conn.execute("SELECT rut, direccion, telefono, email FROM empleado").fetchall()
        for fila in contactos:
            valores = []
            for dato in fila[1:]:
                if dato.startswith("fernet:"):
                    descifrar(dato)
                    valores.append(dato)
                else:
                    valores.append(cifrar(dato))
            conn.execute("UPDATE empleado SET direccion = ?, telefono = ?, email = ? "
                         "WHERE rut = ?", (valores[0], valores[1], valores[2], fila[0]))
