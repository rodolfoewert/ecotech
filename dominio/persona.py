from dominio.validador_entradas import ValidadorEntradas as Validar


class Persona:
    """Conserva el RUT y valida el nombre de una persona."""

    def __init__(self, rut, nombre):
        """El RUT no cambia después de crear la persona."""
        self._rut = Validar.rut(rut)
        self.nombre = nombre

    @property
    def rut(self):
        """Devuelve la identificación de la persona."""
        return self._rut

    @property
    def nombre(self):
        """Devuelve el nombre."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        """Evita nombres vacíos."""
        self._nombre = Validar.texto(valor, "Nombre")
