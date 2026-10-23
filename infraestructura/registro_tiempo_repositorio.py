import sqlite3

from dominio.excepciones import RelacionInvalida
from infraestructura.conexion import obtener_conexion


class RegistroTiempoRepositorio:
    """Guarda jornadas; su lectura se realiza al reconstruir al empleado."""

    def guardar(self, registro):
        """Consulta e inserta bajo el mismo bloqueo para respetar el máximo diario."""
        if registro.id is not None:
            raise ValueError("Ese registro ya está guardado.")
        try:
            with obtener_conexion() as conn:
                conn.execute("BEGIN IMMEDIATE")
                datos = conn.execute("""SELECT e.fecha_ingreso, p.fecha_inicio
                    FROM empleado_proyecto ep
                    JOIN empleado e ON e.rut = ep.empleado_rut
                    JOIN proyecto p ON p.id = ep.proyecto_id
                    WHERE ep.empleado_rut = ? AND ep.proyecto_id = ?""",
                    (registro.empleado.rut, registro.proyecto.id)).fetchone()
                if datos is None:
                    raise RelacionInvalida("Primero debes guardar la asignación al proyecto.")
                fecha = registro.fecha.isoformat()
                if fecha < max(datos):
                    raise RelacionInvalida("La fecha es anterior al ingreso o al proyecto.")
                total = conn.execute("""SELECT COALESCE(SUM(horas), 0) FROM registro_tiempo
                    WHERE empleado_rut = ? AND fecha = ?""",
                    (registro.empleado.rut, fecha)).fetchone()[0]
                if total + registro.horas > 24:
                    raise RelacionInvalida("El empleado superaría las 24 horas diarias.")
                cur = conn.execute("""INSERT INTO registro_tiempo
                    (empleado_rut, proyecto_id, horas, fecha, descripcion)
                    VALUES (?, ?, ?, ?, ?)""", (registro.empleado.rut, registro.proyecto.id,
                    registro.horas, fecha, registro.descripcion))
                identificador = cur.lastrowid
        except sqlite3.IntegrityError as error:
            raise RelacionInvalida("El empleado o proyecto ya no están disponibles.") from error
        registro.id = identificador
        return registro

    def eliminar(self, id):
        """Borra una jornada; recarga al empleado para actualizar sus totales en memoria."""
        with obtener_conexion() as conn:
            cur = conn.execute("DELETE FROM registro_tiempo WHERE id = ?", (id,))
        return cur.rowcount > 0
