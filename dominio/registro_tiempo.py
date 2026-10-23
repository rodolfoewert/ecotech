"""Jornada de un empleado en un proyecto concreto."""

from dominio.validador_entradas import ValidadorEntradas as Validar


class RegistroTiempo:
    """Registro inmutable para conservar consistentes sus relaciones y totales."""

    def __init__(self, fecha, horas, descripcion, empleado, proyecto, id=None):
        """Valida los datos; agregarlo al empleado es una operación separada."""
        from dominio.empleado import Empleado
        from dominio.proyecto import Proyecto
        if not isinstance(empleado, Empleado) or not isinstance(proyecto, Proyecto):
            raise ValueError("Cada registro necesita un empleado y un proyecto válidos.")
        self.id = id
        self._fecha = Validar.fecha(fecha)
        self._horas = Validar.numero(horas, "Horas", estricto=True)
        if self._horas > 24:
            raise ValueError("Una jornada no puede superar las 24 horas.")
        self._descripcion = Validar.texto(descripcion, "Descripción")
        self._empleado = empleado
        self._proyecto = proyecto

    @property
    def fecha(self):
        """Fecha de la jornada."""
        return self._fecha

    @property
    def horas(self):
        """Horas trabajadas."""
        return self._horas

    @property
    def descripcion(self):
        """Actividad realizada."""
        return self._descripcion

    @property
    def empleado(self):
        """Propietario de la jornada."""
        return self._empleado

    @property
    def proyecto(self):
        """Proyecto en el que se trabajó."""
        return self._proyecto

    def ingresar_registro(self):
        """Agrega esta jornada a los objetos relacionados."""
        self.empleado.registrar_hora(self)
        return True

    def __repr__(self):
        """Muestra la jornada y su duración."""
        return f"RegistroTiempo(fecha={self.fecha}, horas={self.horas})"
