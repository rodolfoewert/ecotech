"""Pruebas con una base temporal, sin modificar los datos del usuario."""

import os
import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from dominio.departamento import Departamento
from dominio.empleado import Empleado
from dominio.excepciones import RelacionInvalida, RutDuplicado
from infraestructura.conexion import ErrorDeConexion, obtener_conexion
from infraestructura.departamento_repositorio import DepartamentoRepositorio
from infraestructura.empleado_repositorio import EmpleadoRepositorio
from main import inicializar_bd


class PruebasPersistencia(unittest.TestCase):
    """Comprueba CRUD, integridad y recuperación ante fallos."""

    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.ruta = Path(self.temporal.name) / "prueba.db"
        self.entorno = patch.dict(os.environ, {
            "DB_NOMBRE": str(self.ruta), "DB_MOTOR": "sqlite"
        })
        self.entorno.start()
        self.addCleanup(self.entorno.stop)
        inicializar_bd()
        self.repo = EmpleadoRepositorio()
        self.ana = Empleado("12345678-9", "Ana", date(2024, 3, 1), 950000)

    def test_crud_empleado(self):
        self.repo.guardar(self.ana)
        self.assertEqual(self.repo.obtener(self.ana.rut).nombre, "Ana")
        self.ana.sueldo_base = 1050000
        self.assertEqual(self.repo.actualizar(self.ana), 1)
        self.assertEqual(self.repo.obtener(self.ana.rut).sueldo_base, 1050000)
        self.assertTrue(self.repo.eliminar(self.ana.rut))
        self.assertIsNone(self.repo.obtener(self.ana.rut))
        self.assertFalse(self.repo.eliminar(self.ana.rut))

    def test_crud_departamento(self):
        repo = DepartamentoRepositorio()
        dep = repo.guardar(Departamento("Operaciones"))
        self.assertEqual(repo.obtener(dep.id).nombre, "Operaciones")
        dep.nombre = "Tecnología"
        self.assertEqual(repo.actualizar(dep), 1)
        self.assertEqual(repo.listar("Tecnología")[0].nombre, dep.nombre)
        self.assertTrue(repo.eliminar(dep.id))
        self.assertIsNone(repo.obtener(dep.id))

    def test_inyeccion_no_altera_consultas_ni_borra_datos(self):
        self.repo.guardar(self.ana)
        repo_dep = DepartamentoRepositorio()
        dep = repo_dep.guardar(Departamento("Operaciones"))
        for texto in ("' OR '1'='1", "'; DROP TABLE persona;--"):
            self.assertEqual(self.repo.listar(texto), [])
            self.assertIsNone(self.repo.obtener(texto))
            self.assertFalse(self.repo.eliminar(texto))
            self.assertEqual(repo_dep.listar(texto), [])
            self.assertIsNone(repo_dep.obtener(texto))
            self.assertFalse(repo_dep.eliminar(texto))
        self.assertEqual(len(self.repo.listar()), 1)
        self.assertIsNotNone(repo_dep.obtener(dep.id))

    def test_duplicado_se_distingue_de_conexion(self):
        self.repo.guardar(self.ana)
        with self.assertRaises(RutDuplicado):
            self.repo.guardar(self.ana)
        self.assertEqual(len(self.repo.listar()), 1)

    def test_segunda_escritura_fallida_deshace_la_primera(self):
        with obtener_conexion() as conn:
            conn.execute("""CREATE TRIGGER falla_empleado BEFORE INSERT ON empleado
                            BEGIN SELECT RAISE(ABORT, 'fallo de prueba'); END""")
        with self.assertRaises(RelacionInvalida):
            self.repo.guardar(self.ana)
        with obtener_conexion() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM persona").fetchone()[0], 0)

    def test_error_de_programacion_no_se_disfraza_de_conexion(self):
        with self.assertRaises(ValueError):
            with obtener_conexion() as conn:
                conn.execute("INSERT INTO persona VALUES (?, ?)", ("test", "Test"))
                raise ValueError("fallo de prueba")
        with obtener_conexion() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM persona").fetchone()[0], 0)

    def test_cascada_elimina_los_registros_del_empleado(self):
        self.repo.guardar(self.ana)
        with obtener_conexion() as conn:
            proyecto = conn.execute(
                "INSERT INTO proyecto(nombre, fecha_inicio) VALUES (?, ?)",
                ("Solar", "2026-01-01"),
            ).lastrowid
            conn.execute(
                """INSERT INTO registro_tiempo(empleado_rut, proyecto_id, horas, fecha)
                   VALUES (?, ?, ?, ?)""",
                (self.ana.rut, proyecto, 2, "2026-01-01"),
            )
        self.repo.eliminar(self.ana.rut)
        with obtener_conexion() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM registro_tiempo").fetchone()[0], 0)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM proyecto").fetchone()[0], 1)

    def test_departamento_con_empleados_no_se_borra(self):
        dep = DepartamentoRepositorio().guardar(Departamento("Operaciones"))
        self.repo.guardar(self.ana)
        with obtener_conexion() as conn:
            conn.execute("UPDATE empleado SET departamento_id = ? WHERE rut = ?",
                         (dep.id, self.ana.rut))
        with self.assertRaises(RelacionInvalida):
            DepartamentoRepositorio().eliminar(dep.id)
        self.assertIsNotNone(DepartamentoRepositorio().obtener(dep.id))

    def test_eliminar_empleado_inexistente_no_borra_una_persona(self):
        with obtener_conexion() as conn:
            conn.execute("INSERT INTO persona VALUES (?, ?)", ("persona", "Persona"))
        self.assertFalse(self.repo.eliminar("persona"))
        with obtener_conexion() as conn:
            self.assertIsNotNone(conn.execute(
                "SELECT rut FROM persona WHERE rut = ?", ("persona",)
            ).fetchone())

    def test_configuracion_invalida_tiene_mensaje_claro(self):
        for cambio in ({"DB_NOMBRE": ""}, {"DB_MOTOR": "otro"},
                       {"DB_NOMBRE": str(self.ruta / "no_existe" / "base.db")}):
            with patch.dict(os.environ, cambio):
                with self.assertRaises(ErrorDeConexion):
                    with obtener_conexion():
                        self.fail("No debe abrir una conexión inválida")

    def test_esquema_se_puede_ejecutar_dos_veces(self):
        inicializar_bd()
        self.assertEqual(self.repo.listar(), [])


if __name__ == "__main__":
    unittest.main()
