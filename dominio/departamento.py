"""Departamento y asignación exclusiva de empleados."""

from dominio.validador_entradas import ValidadorEntradas as Validar


class Departamento:
    """Agrupa empleados sin ser dueño de su ciclo de vida."""

    def __init__(self, nombre, id=None, gerente=""):
        """El identificador se asigna al guardar en la base."""
        self.id = id
        self.nombre = nombre
        self.gerente = gerente
        self._empleados = []

    @property
    def nombre(self):
        """Nombre del área."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        """Evita departamentos sin nombre."""
        self._nombre = Validar.texto(valor, "Departamento")

    @property
    def gerente(self):
        """Nombre del responsable, sin crear una subclase Gerente."""
        return self._gerente

    @gerente.setter
    def gerente(self, valor):
        """Normaliza el nombre del responsable."""
        self._gerente = Validar.sanitizar_texto(valor)

    @property
    def empleados(self):
        """Devuelve los empleados asignados."""
        return tuple(self._empleados)

    def asignar_empleado(self, empleado):
        """Mueve al empleado del departamento anterior a este."""
        from dominio.empleado import Empleado
        if not isinstance(empleado, Empleado):
            raise ValueError("Se esperaba un empleado.")
        if empleado.departamento is self:
            return False
        if any(e.rut == empleado.rut for e in self._empleados):
            raise ValueError("Ya hay otro objeto con ese RUT en el departamento.")
        if empleado.departamento is not None:
            empleado.departamento._empleados.remove(empleado)
        self._empleados.append(empleado)
        empleado._departamento = self
        return True

    def agregar_empleado(self, empleado):
        """Conserva el nombre utilizado en el laboratorio C05."""
        return self.asignar_empleado(empleado)

    def __repr__(self):
        """Representación legible para la consola."""
        return f"Departamento(id={self.id}, nombre={self.nombre!r})"
