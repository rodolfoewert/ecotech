"""Proyecto con participantes y registros de horas."""

from dominio.validador_entradas import ValidadorEntradas as Validar


class Proyecto:
    """Representa una iniciativa y calcula el esfuerzo registrado."""

    def __init__(self, id, nombre, fecha_inicio, descripcion=""):
        """Inicializa todas las colecciones del proyecto."""
        self.id = id
        self.nombre = nombre
        self.fecha_inicio = fecha_inicio
        self.descripcion = descripcion
        self._registros = []
        self._empleados = []
        self.informes = []

    @property
    def nombre(self):
        """Nombre del proyecto."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        """Exige un nombre no vacío."""
        self._nombre = Validar.texto(valor, "Proyecto")

    @property
    def fecha_inicio(self):
        """Fecha desde la cual se pueden registrar horas."""
        return self._fecha_inicio

    @fecha_inicio.setter
    def fecha_inicio(self, valor):
        """Exige un objeto date."""
        self._fecha_inicio = Validar.fecha(valor)

    @property
    def descripcion(self):
        """Descripción de la iniciativa."""
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor):
        """Normaliza la descripción opcional."""
        self._descripcion = Validar.sanitizar_texto(valor)

    @property
    def empleados(self):
        """Participantes asignados."""
        return tuple(self._empleados)

    @property
    def registros(self):
        """Jornadas registradas en el proyecto."""
        return tuple(self._registros)

    def asignar_empleado(self, empleado):
        """Delega la asignación para actualizar ambos lados de la relación."""
        from dominio.empleado import Empleado
        if not isinstance(empleado, Empleado):
            raise ValueError("Se esperaba un empleado.")
        empleado.asignar_proyecto(self)

    def agregar_registro(self, registro):
        """Valida la jornada mediante el empleado que la realiza."""
        from dominio.registro_tiempo import RegistroTiempo
        if not isinstance(registro, RegistroTiempo) or registro.proyecto is not self:
            raise ValueError("El registro no pertenece a este proyecto.")
        registro.empleado.registrar_hora(registro)

    def total_horas(self):
        """Suma el tiempo dedicado a este proyecto."""
        return sum(registro.horas for registro in self._registros)

    def __repr__(self):
        """Representación para la demostración."""
        return f"Proyecto(id={self.id}, nombre={self.nombre!r})"
