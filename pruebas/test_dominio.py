"""Comportamiento del modelo sin acceder a la base de datos."""

import unittest
from datetime import date

from dominio.departamento import Departamento
from dominio.empleado import Empleado
from dominio.empleado_planta import EmpleadoPlanta
from dominio.empleado_contratista import EmpleadoContratista
from dominio.informe import Informe
from dominio.proyecto import Proyecto
from dominio.registro_tiempo import RegistroTiempo


class PruebasDominio(unittest.TestCase):
    """Verifica validaciones, relaciones y polimorfismo."""

    def setUp(self):
        self.ana = EmpleadoPlanta("12345678-9", "Ana", date(2024, 1, 1), 900000,
                                  bono_sostenibilidad=100000)
        self.proyecto = Proyecto(None, "Solar", date(2026, 1, 1))

    def test_empleado_es_abstracto(self):
        with self.assertRaises(TypeError):
            Empleado("12345678-9", "Ana", date(2024, 1, 1), 900000)

    def test_datos_invalidos_no_reemplazan_valores_anteriores(self):
        for valor in (-1, 0, True, float("nan"), float("inf"), "1000"):
            with self.subTest(valor=valor):
                with self.assertRaises(ValueError):
                    self.ana.sueldo_base = valor
                self.assertEqual(self.ana.sueldo_base, 900000)
        for campo, valor in (("nombre", " "), ("email", "sin arroba"),
                             ("telefono", "hola"), ("fecha_ingreso", "2026-01-01")):
            with self.assertRaises(ValueError):
                setattr(self.ana, campo, valor)
        with self.assertRaises(AttributeError):
            self.ana.rut = "11111111-1"

    def test_reasignar_departamento_actualiza_ambos_lados(self):
        anterior = Departamento("Operaciones")
        nuevo = Departamento("Tecnología")
        anterior.asignar_empleado(self.ana)
        nuevo.asignar_empleado(self.ana)
        self.assertEqual(anterior.empleados, ())
        self.assertEqual(nuevo.empleados, (self.ana,))
        self.assertIs(self.ana.departamento, nuevo)
        self.assertFalse(nuevo.asignar_empleado(self.ana))

    def test_pago_segun_tipo_de_contrato_y_horas(self):
        otro = EmpleadoContratista("11111111-1", "Luis", date(2024, 1, 1),
                                   900000, tarifa_hora=10000)
        otro.asignar_proyecto(self.proyecto)
        RegistroTiempo(date(2026, 1, 2), 3.5, "Desarrollo", otro,
                       self.proyecto).ingresar_registro()
        self.assertEqual([e.calcular_pago() for e in (self.ana, otro)], [1000000, 35000])
        self.assertEqual(self.proyecto.total_horas(), 3.5)
        self.assertEqual(otro.total_horas(), 3.5)
        self.assertIn(otro, self.proyecto.empleados)

    def test_registro_exige_asignacion_y_no_se_agrega_dos_veces(self):
        registro = RegistroTiempo(date(2026, 1, 2), 8, "Desarrollo", self.ana,
                                  self.proyecto)
        with self.assertRaises(ValueError):
            registro.ingresar_registro()
        self.ana.asignar_proyecto(self.proyecto)
        registro.ingresar_registro()
        with self.assertRaises(ValueError):
            registro.ingresar_registro()
        self.assertEqual(self.ana.total_horas(), 8)
        self.assertEqual(self.proyecto.total_horas(), 8)

    def test_jornadas_respetan_fechas_y_limite_diario(self):
        self.ana.asignar_proyecto(self.proyecto)
        for horas in (0, -1, 25, float("inf"), True):
            with self.assertRaises(ValueError):
                RegistroTiempo(date(2026, 1, 2), horas, "Trabajo", self.ana, self.proyecto)
        with self.assertRaises(ValueError):
            RegistroTiempo(date(2025, 1, 1), 2, "Trabajo", self.ana,
                           self.proyecto).ingresar_registro()
        RegistroTiempo(date(2026, 1, 2), 20, "Trabajo", self.ana,
                       self.proyecto).ingresar_registro()
        otro = Proyecto(None, "Eólico", date(2026, 1, 1))
        self.ana.asignar_proyecto(otro)
        with self.assertRaises(ValueError):
            RegistroTiempo(date(2026, 1, 2), 5, "Trabajo", self.ana, otro).ingresar_registro()
        self.assertEqual(self.ana.total_horas(), 20)
        self.assertEqual(otro.total_horas(), 0)

    def test_informe_usa_horas_reales_del_proyecto(self):
        informe = Informe("Avance", date(2026, 1, 2))
        with self.assertRaises(ValueError):
            informe.generar()
        informe.proyecto = self.proyecto
        self.assertIn("Horas registradas: 0", informe.generar())
