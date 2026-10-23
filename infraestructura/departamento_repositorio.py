import sqlite3
from dominio.departamento import Departamento
from dominio.excepciones import RelacionInvalida
from infraestructura.conexion import obtener_conexion

class DepartamentoRepositorio:
    """CRUD de departamentos; no permite borrar áreas con empleados."""

    @staticmethod
    def _fila_a_departamento(fila):
        """Reconstruye un departamento desde la consulta."""
        return Departamento(id=fila[0], nombre=fila[1], gerente=fila[2])

    def guardar(self, departamento: Departamento):
        """Guarda un departamento nuevo."""
        if departamento.id is not None:
            raise ValueError("El departamento ya tiene un identificador.")
        with obtener_conexion() as conn:
            cur = conn.execute(
                "INSERT INTO departamento (nombre, gerente) VALUES (?, ?)",
                (departamento.nombre, departamento.gerente),
            )
            identificador = cur.lastrowid
        departamento.id = identificador
        return departamento

    def obtener(self, id: int):
        """Busca un departamento por su identificador."""
        with obtener_conexion() as conn:
            fila = conn.execute(
                "SELECT id, nombre, gerente FROM departamento WHERE id = ?",
                (id,),
            ).fetchone()
        return self._fila_a_departamento(fila) if fila else None

    def listar(self, nombre_contiene=None):
        """Lista departamentos con un filtro opcional."""
        sql = "SELECT id, nombre, gerente FROM departamento"
        params = []
        if nombre_contiene:
            sql += " WHERE nombre LIKE ?"
            params.append(f"%{nombre_contiene}%")
        with obtener_conexion() as conn:
            filas = conn.execute(sql, params).fetchall()
        return [self._fila_a_departamento(f) for f in filas]

    def actualizar(self, departamento: Departamento):
        """Actualiza nombre y responsable."""
        with obtener_conexion() as conn:
            cur = conn.execute(
                "UPDATE departamento SET nombre = ?, gerente = ? WHERE id = ?",
                (departamento.nombre, departamento.gerente, departamento.id),
            )
        return cur.rowcount

    def eliminar(self, id: int):
        """Borra un departamento que no tiene empleados."""
        try:
            with obtener_conexion() as conn:
                cur = conn.execute("DELETE FROM departamento WHERE id = ?", (id,))
        except sqlite3.IntegrityError as error:
            raise RelacionInvalida(
                "No puedes eliminar un departamento que tiene empleados."
            ) from error
        return cur.rowcount > 0
