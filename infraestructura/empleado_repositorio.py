import sqlite3
from datetime import date

from dominio.departamento import Departamento
from dominio.empleado_planta import EmpleadoPlanta
from dominio.empleado_contratista import EmpleadoContratista
from dominio.excepciones import RutDuplicado, RelacionInvalida
from dominio.proyecto import Proyecto
from dominio.registro_tiempo import RegistroTiempo
from infraestructura.conexion import obtener_conexion
from seguridad.cifrado import cifrar, descifrar

CONSULTA = """SELECT p.rut, p.nombre, e.fecha_ingreso, e.sueldo_base,
              e.direccion, e.telefono, e.email, e.tipo_contrato, e.bono, e.tarifa,
              d.id, d.nombre, d.gerente
              FROM empleado e JOIN persona p ON p.rut = e.rut
              LEFT JOIN departamento d ON d.id = e.departamento_id"""


class EmpleadoRepositorio:
    """Traduce objetos a filas y reconstruye su tipo de contrato."""

    @staticmethod
    def _fila_a_empleado(fila):
        """Mantiene el mapeo del empleado en un solo lugar."""
        rut = fila[0]
        nombre = fila[1]
        fecha = date.fromisoformat(fila[2])
        sueldo = fila[3]
        direccion = descifrar(fila[4])
        telefono = descifrar(fila[5])
        correo = descifrar(fila[6])
        tipo = fila[7]
        if tipo == "planta":
            empleado = EmpleadoPlanta(rut, nombre, fecha, sueldo, fila[8],
                                      direccion, telefono, correo)
        elif tipo == "contratista":
            empleado = EmpleadoContratista(rut, nombre, fecha, sueldo, fila[9],
                                           direccion, telefono, correo)
        else:
            raise ValueError("La base contiene un tipo de contrato desconocido.")
        if fila[10] is not None:
            Departamento(fila[11], id=fila[10], gerente=fila[12]).asignar_empleado(empleado)
        return empleado

    @staticmethod
    def _parametros(empleado):
        """Solo acepta los contratos implementados y devuelve sus datos."""
        if isinstance(empleado, EmpleadoPlanta):
            tipo, bono, tarifa = "planta", empleado.bono_sostenibilidad, 0
        elif isinstance(empleado, EmpleadoContratista):
            tipo, bono, tarifa = "contratista", 0, empleado.tarifa_hora
        else:
            raise ValueError("El empleado debe ser de planta o contratista.")
        departamento_id = None
        if empleado.departamento is not None:
            departamento_id = empleado.departamento.id
            if departamento_id is None:
                raise RelacionInvalida("Primero debes guardar el departamento.")
        return (empleado.fecha_ingreso.isoformat(), empleado.sueldo_base,
                cifrar(empleado.direccion), cifrar(empleado.telefono), cifrar(empleado.email),
                tipo, bono, tarifa, departamento_id)

    def guardar(self, empleado):
        """Guarda persona y empleado en una única transacción."""
        datos = self._parametros(empleado)
        try:
            with obtener_conexion() as conn:
                conn.execute("INSERT INTO persona (rut, nombre) VALUES (?, ?)",
                             (empleado.rut, empleado.nombre))
                conn.execute("""INSERT INTO empleado
                    (rut, fecha_ingreso, sueldo_base, direccion, telefono, email,
                     tipo_contrato, bono, tarifa, departamento_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (empleado.rut,) + datos)
        except sqlite3.IntegrityError as error:
            if error.sqlite_errorname in ("SQLITE_CONSTRAINT_PRIMARYKEY",
                                          "SQLITE_CONSTRAINT_UNIQUE"):
                raise RutDuplicado("Ya existe una persona con ese RUT.") from error
            raise RelacionInvalida("No se pudo guardar el empleado y sus relaciones.") from error
        return empleado

    @staticmethod
    def _cargar_relaciones(conn, empleado):
        """Carga proyectos y jornadas para que total_horas y calcular_pago sean reales."""
        proyectos = {}
        filas = conn.execute("""SELECT p.id, p.nombre, p.fecha_inicio, p.descripcion
            FROM proyecto p JOIN empleado_proyecto ep ON ep.proyecto_id = p.id
            WHERE ep.empleado_rut = ? ORDER BY p.id""", (empleado.rut,)).fetchall()
        for fila in filas:
            proyecto = Proyecto(fila[0], fila[1], date.fromisoformat(fila[2]), fila[3])
            empleado.asignar_proyecto(proyecto)
            proyectos[proyecto.id] = proyecto
        filas = conn.execute("""SELECT id, fecha, horas, descripcion, proyecto_id
            FROM registro_tiempo WHERE empleado_rut = ? ORDER BY fecha, id""",
                             (empleado.rut,)).fetchall()
        for fila in filas:
            proyecto = proyectos.get(fila[4])
            if proyecto is None:
                raise RelacionInvalida("Hay una jornada sin asignación al proyecto.")
            registro = RegistroTiempo(date.fromisoformat(fila[1]), fila[2],
                fila[3] or "Registro anterior sin descripción", empleado, proyecto, id=fila[0])
            empleado.registrar_hora(registro)
        return empleado

    def obtener(self, rut):
        """Devuelve un empleado completo o None si no existe."""
        sql = CONSULTA
        sql += " WHERE e.rut = ?"
        with obtener_conexion() as conn:
            fila = conn.execute(sql, (rut,)).fetchone()
            if fila is None:
                return None
            empleado = self._fila_a_empleado(fila)
            return self._cargar_relaciones(conn, empleado)

    def listar(self, nombre_contiene=None):
        """Busca por nombre sin interpretar el filtro como SQL."""
        sql, parametros = CONSULTA, []
        if nombre_contiene:
            sql += " WHERE p.nombre LIKE ?"
            parametros.append(f"%{nombre_contiene}%")
        sql += " ORDER BY p.rut"
        with obtener_conexion() as conn:
            filas = conn.execute(sql, parametros).fetchall()
            empleados = []
            for fila in filas:
                empleado = self._fila_a_empleado(fila)
                self._cargar_relaciones(conn, empleado)
                empleados.append(empleado)
            return empleados

    def actualizar(self, empleado):
        """Actualiza los datos del contrato y el nombre en una sola transacción."""
        datos = self._parametros(empleado)
        try:
            with obtener_conexion() as conn:
                anterior = conn.execute("SELECT MIN(fecha) FROM registro_tiempo "
                    "WHERE empleado_rut = ?", (empleado.rut,)).fetchone()[0]
                if anterior and empleado.fecha_ingreso.isoformat() > anterior:
                    raise RelacionInvalida("El ingreso no puede ser posterior a sus jornadas.")
                cur = conn.execute("""UPDATE empleado
                    SET fecha_ingreso = ?, sueldo_base = ?,
                    direccion = ?, telefono = ?, email = ?, tipo_contrato = ?, bono = ?,
                    tarifa = ?, departamento_id = ? WHERE rut = ?""", datos + (empleado.rut,))
                if cur.rowcount:
                    conn.execute("UPDATE persona SET nombre = ? WHERE rut = ?",
                                 (empleado.nombre, empleado.rut))
                return cur.rowcount
        except sqlite3.IntegrityError as error:
            raise RelacionInvalida("El departamento no existe o los datos son inválidos.") from error

    def asignar_proyecto(self, empleado, proyecto):
        """Persiste la relación N:M y luego actualiza ambos objetos."""
        if proyecto.id is None:
            raise RelacionInvalida("Primero debes guardar el proyecto.")
        try:
            with obtener_conexion() as conn:
                cur = conn.execute("""INSERT OR IGNORE INTO empleado_proyecto
                    (empleado_rut, proyecto_id) VALUES (?, ?)""", (empleado.rut, proyecto.id))
        except sqlite3.IntegrityError as error:
            raise RelacionInvalida("El empleado o el proyecto no están guardados.") from error
        empleado.asignar_proyecto(proyecto)
        return cur.rowcount > 0

    def eliminar(self, rut):
        """Borra al empleado, sus jornadas y sus asignaciones por cascada."""
        with obtener_conexion() as conn:
            cur = conn.execute("DELETE FROM empleado WHERE rut = ?", (rut,))
            if cur.rowcount:
                conn.execute("DELETE FROM persona WHERE rut = ?", (rut,))
        return cur.rowcount > 0
