"""CRUD de proyectos, separado del modelo de negocio."""

import sqlite3
from datetime import date

from dominio.excepciones import RelacionInvalida
from dominio.proyecto import Proyecto
from infraestructura.conexion import obtener_conexion


class ProyectoRepositorio:
    """Guarda los datos del proyecto; las jornadas se cargan mediante los empleados."""

    @staticmethod
    def _fila_a_proyecto(fila):
        """Reconstruye los datos propios del proyecto, sin cargar sus participantes."""
        return Proyecto(fila[0], fila[1], date.fromisoformat(fila[2]), fila[3])

    def guardar(self, proyecto):
        """Guarda un proyecto nuevo y asigna su id después del commit."""
        if proyecto.id is not None:
            raise ValueError("El proyecto ya tiene un identificador.")
        with obtener_conexion() as conn:
            cur = conn.execute("""INSERT INTO proyecto(nombre, fecha_inicio, descripcion)
                VALUES (?, ?, ?)""", (proyecto.nombre, proyecto.fecha_inicio.isoformat(),
                                     proyecto.descripcion))
            identificador = cur.lastrowid
        proyecto.id = identificador
        return proyecto

    def obtener(self, id):
        """Devuelve los datos propios de un proyecto o None."""
        with obtener_conexion() as conn:
            fila = conn.execute("SELECT id, nombre, fecha_inicio, descripcion "
                                "FROM proyecto WHERE id = ?", (id,)).fetchone()
        return self._fila_a_proyecto(fila) if fila else None

    def listar(self, nombre_contiene=None):
        """Lista proyectos y permite filtrar sus nombres."""
        sql = "SELECT id, nombre, fecha_inicio, descripcion FROM proyecto"
        parametros = []
        if nombre_contiene:
            sql += " WHERE nombre LIKE ?"
            parametros.append(f"%{nombre_contiene}%")
        with obtener_conexion() as conn:
            filas = conn.execute(sql + " ORDER BY id", parametros).fetchall()
        return [self._fila_a_proyecto(fila) for fila in filas]

    def actualizar(self, proyecto):
        """Impide que una nueva fecha invalide jornadas existentes."""
        with obtener_conexion() as conn:
            primera = conn.execute("SELECT MIN(fecha) FROM registro_tiempo "
                "WHERE proyecto_id = ?", (proyecto.id,)).fetchone()[0]
            if primera and proyecto.fecha_inicio.isoformat() > primera:
                raise RelacionInvalida("El inicio no puede ser posterior a las jornadas.")
            cur = conn.execute("UPDATE proyecto SET nombre = ?, fecha_inicio = ?, "
                "descripcion = ? WHERE id = ?", (proyecto.nombre,
                proyecto.fecha_inicio.isoformat(), proyecto.descripcion, proyecto.id))
        return cur.rowcount

    def eliminar(self, id):
        """Conserva proyectos que tienen jornadas o informes asociados."""
        try:
            with obtener_conexion() as conn:
                cur = conn.execute("DELETE FROM proyecto WHERE id = ?", (id,))
        except sqlite3.IntegrityError as error:
            raise RelacionInvalida("El proyecto tiene jornadas o informes asociados.") from error
        return cur.rowcount > 0
