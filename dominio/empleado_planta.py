"""Empleado con sueldo base y bono de sostenibilidad."""

from dominio.empleado import Empleado
from dominio.validador_entradas import ValidadorEntradas as Validar


class EmpleadoPlanta(Empleado):
    """Especializa el pago de un trabajador de planta."""

    def __init__(self, rut, nombre, fecha_ingreso, sueldo_base,
                 bono_sostenibilidad=0, **contacto):
        """Reutiliza los datos comunes de Empleado."""
        super().__init__(rut, nombre, fecha_ingreso, sueldo_base, **contacto)
        self.bono_sostenibilidad = bono_sostenibilidad

    @property
    def bono_sostenibilidad(self):
        """Bono que se suma al sueldo base."""
        return self._bono_sostenibilidad

    @bono_sostenibilidad.setter
    def bono_sostenibilidad(self, valor):
        """El bono puede ser cero, pero no negativo."""
        self._bono_sostenibilidad = Validar.numero(valor, "Bono")

    def calcular_pago(self):
        """Calcula el pago bruto, sin descuentos legales."""
        return self.sueldo_base + self.bono_sostenibilidad
