from infraestructura.conexion import obtener_conexion

# Inserción de prueba
with obtener_conexion() as conn:
    conn.execute(
        "INSERT OR IGNORE INTO persona (rut, nombre) VALUES (?, ?)",
        ("12345678-9", "Ana Rojas"),
    )

# Lectura de prueba
with obtener_conexion() as conn:
    filas = conn.execute("SELECT rut, nombre FROM persona").fetchall()
    print("Resultado en base de datos:")
    for fila in filas:
        print(fila)