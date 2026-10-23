from dominio.empleado import Empleado
from dominio.validador_entradas import ValidadorEntradas as Validar


class EmpleadoContratista(Empleado):
    """Calcula un pago bruto por hora; no suma el sueldo base de referencia."""

    def __init__(self, rut, nombre, fecha_ingreso, sueldo_base, tarifa_hora,
                 direccion="", telefono="", email=""):
        """Reutiliza los datos comunes y exige una tarifa positiva."""
        super().__init__(rut, nombre, fecha_ingreso, sueldo_base,
                         direccion, telefono, email)
        self.tarifa_hora = tarifa_hora

    @property
    def tarifa_hora(self):
        """Monto por cada hora registrada."""
        return self._tarifa_hora

    @tarifa_hora.setter
    def tarifa_hora(self, valor):
        """No admite una tarifa nula o negativa."""
        self._tarifa_hora = Validar.numero(valor, "Tarifa", estricto=True)

    def calcular_pago(self):
        """Calcula el pago por todas las horas cargadas en este objeto."""
        return self.tarifa_hora * self.total_horas()
