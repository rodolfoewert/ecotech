"""Pruebas de contratos, relaciones y actualización del esquema anterior."""

import os
from contextlib import closing
import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch
from cryptography.fernet import Fernet

from dominio.departamento import Departamento
from dominio.empleado_contratista import EmpleadoContratista
from dominio.empleado_planta import EmpleadoPlanta
from dominio.excepciones import RelacionInvalida
from dominio.proyecto import Proyecto
from dominio.registro_tiempo import RegistroTiempo
from infraestructura.conexion import obtener_conexion
from infraestructura.departamento_repositorio import DepartamentoRepositorio
from infraestructura.empleado_repositorio import EmpleadoRepositorio
from infraestructura.esquema import inicializar_bd
from infraestructura.proyecto_repositorio import ProyectoRepositorio
from infraestructura.registro_tiempo_repositorio import RegistroTiempoRepositorio


class PruebasRelacionesBD(unittest.TestCase):
    """Verifica que guardar y recargar conserve el comportamiento del modelo."""

    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.ruta = Path(temporal.name) / "ecotech.db"
        entorno = patch.dict(os.environ, {"DB_NOMBRE": str(self.ruta), "DB_MOTOR": "sqlite",
            "CLAVE_CIFRADO": Fernet.generate_key().decode("ascii")})
        entorno.start()
        self.addCleanup(entorno.stop)
        inicializar_bd()
        self.repo = EmpleadoRepositorio()
        self.proyectos = ProyectoRepositorio()
        self.registros = RegistroTiempoRepositorio()
        self.empleado = EmpleadoContratista("11111111-1", "Luis", date(2024, 1, 1),
                                            900000, 10000, email="luis@ejemplo.cl")
        self.depto = DepartamentoRepositorio().guardar(Departamento("Desarrollo", gerente="Ana"))
        self.depto.asignar_empleado(self.empleado)
        self.repo.guardar(self.empleado)
        self.proyecto = self.proyectos.guardar(Proyecto(None, "Solar", date(2026, 1, 1)))

    def jornada(self, horas=3):
        return RegistroTiempo(date(2026, 1, 2), horas, "Desarrollo", self.empleado, self.proyecto)

    def test_recargar_contrato_contacto_y_departamento(self):
        leido = self.repo.obtener(self.empleado.rut)
        self.assertIsInstance(leido, EmpleadoContratista)
        self.assertEqual(leido.tarifa_hora, 10000)
        self.assertEqual(leido.email, "luis@ejemplo.cl")
        self.assertEqual(leido.departamento.id, self.depto.id)
        self.assertEqual(leido.departamento.gerente, "Ana")
        planta = EmpleadoPlanta("12345678-9", "Ana", date(2024, 1, 1), 900000, 100000)
        self.repo.guardar(planta)
        self.assertEqual(self.repo.obtener(planta.rut).calcular_pago(), 1000000)

    def test_asignacion_y_horas_se_conservan_al_recargar(self):
        self.assertTrue(self.repo.asignar_proyecto(self.empleado, self.proyecto))
        self.assertFalse(self.repo.asignar_proyecto(self.empleado, self.proyecto))
        registro = self.registros.guardar(self.jornada(3.5))
        with self.assertRaises(ValueError):
            self.registros.guardar(registro)
        leido = self.repo.obtener(self.empleado.rut)
        self.assertEqual(leido.total_horas(), 3.5)
        self.assertEqual(leido.calcular_pago(), 35000)
        self.assertEqual(leido.proyectos[0].total_horas(), 3.5)
        self.assertEqual(leido.registros[0].descripcion, "Desarrollo")
        self.assertEqual(self.repo.listar()[0].calcular_pago(), 35000)

    def test_no_guarda_jornadas_sin_asignacion_o_con_exceso_de_horas(self):
        with self.assertRaises(RelacionInvalida):
            self.registros.guardar(self.jornada())
        self.repo.asignar_proyecto(self.empleado, self.proyecto)
        self.registros.guardar(self.jornada(20))
        with self.assertRaises(RelacionInvalida):
            self.registros.guardar(self.jornada(5))
        self.assertEqual(self.repo.obtener(self.empleado.rut).total_horas(), 20)
        with self.assertRaises(RelacionInvalida):
            self.registros.guardar(RegistroTiempo(date(2025, 1, 1), 1, "Trabajo",
                                                  self.empleado, self.proyecto))

    def test_actualizar_conserva_todos_los_campos(self):
        self.empleado.nombre = "Luis Pérez"
        self.empleado.tarifa_hora = 12000
        self.empleado.telefono = "+56912345678"
        self.empleado.email = "nuevo@ejemplo.cl"
        self.assertEqual(self.repo.actualizar(self.empleado), 1)
        leido = self.repo.obtener(self.empleado.rut)
        self.assertEqual(leido.nombre, "Luis Pérez")
        self.assertEqual(leido.tarifa_hora, 12000)
        self.assertEqual(leido.telefono, "+56912345678")
        self.assertEqual(leido.email, "nuevo@ejemplo.cl")

    def test_proyecto_crud_e_inyeccion(self):
        self.proyecto.nombre = "Eólico"
        self.proyecto.descripcion = "Nueva descripción"
        self.assertEqual(self.proyectos.actualizar(self.proyecto), 1)
        self.assertEqual(self.proyectos.obtener(self.proyecto.id).descripcion, "Nueva descripción")
        self.assertEqual(len(self.proyectos.listar("Eólico")), 1)
        for texto in ("' OR '1'='1", "'; DROP TABLE proyecto;--"):
            self.assertIsNone(self.proyectos.obtener(texto))
            self.assertEqual(self.proyectos.listar(texto), [])
            self.assertFalse(self.proyectos.eliminar(texto))
        self.assertTrue(self.proyectos.eliminar(self.proyecto.id))

    def test_fechas_editadas_no_invalidan_jornadas_guardadas(self):
        self.repo.asignar_proyecto(self.empleado, self.proyecto)
        self.registros.guardar(self.jornada())
        self.proyecto.fecha_inicio = date(2026, 2, 1)
        with self.assertRaises(RelacionInvalida):
            self.proyectos.actualizar(self.proyecto)
        self.empleado.fecha_ingreso = date(2026, 2, 1)
        with self.assertRaises(RelacionInvalida):
            self.repo.actualizar(self.empleado)
        self.assertEqual(self.repo.obtener(self.empleado.rut).total_horas(), 3)

    def test_cascada_y_restriccion_de_proyecto(self):
        self.repo.asignar_proyecto(self.empleado, self.proyecto)
        self.registros.guardar(self.jornada())
        with self.assertRaises(RelacionInvalida):
            self.proyectos.eliminar(self.proyecto.id)
        self.repo.eliminar(self.empleado.rut)
        with obtener_conexion() as conn:
            total = conn.execute("SELECT COUNT(*) FROM empleado_proyecto").fetchone()[0]
            self.assertEqual(total, 0)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM registro_tiempo").fetchone()[0], 0)
        self.assertIsNotNone(self.proyectos.obtener(self.proyecto.id))

    def test_migracion_conserva_datos_del_esquema_de_clase(self):
        antigua = self.ruta.parent / "antigua.db"
        with closing(sqlite3.connect(antigua)) as conn:
            conn.executescript("""
                CREATE TABLE persona(rut TEXT PRIMARY KEY, nombre TEXT NOT NULL);
                CREATE TABLE departamento(id INTEGER PRIMARY KEY, nombre TEXT NOT NULL);
                CREATE TABLE empleado(rut TEXT PRIMARY KEY, fecha_ingreso TEXT NOT NULL,
                    sueldo_base INTEGER NOT NULL, departamento_id INTEGER);
                CREATE TABLE proyecto(id INTEGER PRIMARY KEY, nombre TEXT NOT NULL,
                    fecha_inicio TEXT NOT NULL);
                CREATE TABLE registro_tiempo(id INTEGER PRIMARY KEY, empleado_rut TEXT,
                    proyecto_id INTEGER, horas REAL, fecha TEXT);
                INSERT INTO persona VALUES ('12345678-9', 'Ana');
                INSERT INTO empleado VALUES ('12345678-9', '2024-01-01', 900000, NULL);
                INSERT INTO proyecto VALUES (1, 'Solar', '2026-01-01');
                INSERT INTO registro_tiempo VALUES (1, '12345678-9', 1, 3, '2026-01-02');
            """)
        with patch.dict(os.environ, {"DB_NOMBRE": str(antigua)}):
            inicializar_bd()
            inicializar_bd()
            leido = self.repo.obtener("12345678-9")
            self.assertIsInstance(leido, EmpleadoPlanta)
            self.assertEqual(leido.total_horas(), 3)
            self.assertEqual(leido.nombre, "Ana")
