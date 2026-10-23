from pathlib import Path

from infraestructura.conexion import obtener_conexion
from seguridad.cifrado import cifrar, descifrar


CAMBIOS = [
    ("PRAGMA table_info(departamento)", [
        ("gerente", "ALTER TABLE departamento ADD COLUMN gerente TEXT NOT NULL DEFAULT ''")
    ]),
    ("PRAGMA table_info(proyecto)", [
        ("descripcion", "ALTER TABLE proyecto ADD COLUMN descripcion TEXT NOT NULL DEFAULT ''")
    ]),
    ("PRAGMA table_info(registro_tiempo)", [
        ("descripcion",
         "ALTER TABLE registro_tiempo ADD COLUMN descripcion TEXT NOT NULL DEFAULT ''")
    ]),
    ("PRAGMA table_info(empleado)", [
        ("direccion", "ALTER TABLE empleado ADD COLUMN direccion TEXT NOT NULL DEFAULT ''"),
        ("telefono", "ALTER TABLE empleado ADD COLUMN telefono TEXT NOT NULL DEFAULT ''"),
        ("email", "ALTER TABLE empleado ADD COLUMN email TEXT NOT NULL DEFAULT ''"),
        ("tipo_contrato",
         "ALTER TABLE empleado ADD COLUMN tipo_contrato TEXT NOT NULL DEFAULT 'planta'"),
        ("bono", "ALTER TABLE empleado ADD COLUMN bono REAL NOT NULL DEFAULT 0"),
        ("tarifa", "ALTER TABLE empleado ADD COLUMN tarifa REAL NOT NULL DEFAULT 0"),
    ]),
]


def inicializar_bd():
    """Inicializa una base nueva o agrega columnas a la versión usada en clase."""
    ruta = Path(__file__).resolve().parent.parent / "db" / "01_esquema.sql"
    with obtener_conexion() as conn:
        conn.executescript("BEGIN;\n" + ruta.read_text(encoding="utf-8"))
        for consulta_columnas, cambios in CAMBIOS:
            columnas = []
            for fila in conn.execute(consulta_columnas):
                columnas.append(fila[1])
            for nombre, sentencia in cambios:
                if nombre not in columnas:
                    conn.execute(sentencia)
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
