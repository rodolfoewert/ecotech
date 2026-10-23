from abc import ABC, abstractmethod

from dominio.persona import Persona
from dominio.validador_entradas import ValidadorEntradas as Validar


class Empleado(Persona, ABC):
    """Empleado con datos validados, departamento, proyectos y registros de horas."""

    def __init__(self, rut, nombre, fecha_ingreso, sueldo_base,
                 direccion="", telefono="", email=""):
        """Inicializa los datos comunes sin incorporar SQL al dominio."""
        super().__init__(rut, nombre)
        self.fecha_ingreso = fecha_ingreso
        self.sueldo_base = sueldo_base
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self._departamento = None
        self._registros = []
        self._proyectos = []

    @property
    def fecha_ingreso(self):
        """Fecha de incorporación."""
        return self._fecha_ingreso

    @fecha_ingreso.setter
    def fecha_ingreso(self, valor):
        """Exige una fecha válida."""
        self._fecha_ingreso = Validar.fecha(valor)

    @property
    def sueldo_base(self):
        """Sueldo antes de bonos o del cálculo por horas."""
        return self._sueldo_base

    @sueldo_base.setter
    def sueldo_base(self, valor):
        """Un sueldo base debe ser positivo."""
        self._sueldo_base = Validar.numero(valor, "Sueldo", estricto=True)

    @property
    def direccion(self):
        """Dirección de contacto opcional."""
        return self._direccion

    @direccion.setter
    def direccion(self, valor):
        """Normaliza el texto sin inventar datos de contacto."""
        self._direccion = Validar.sanitizar_texto(valor)

    @property
    def telefono(self):
        """Teléfono de contacto opcional."""
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        """Valida el teléfono cuando se informa."""
        valor = Validar.sanitizar_texto(valor)
        if valor and not Validar.validar_telefono(valor):
            raise ValueError("El teléfono debe contener entre 8 y 15 dígitos.")
        self._telefono = valor

    @property
    def email(self):
        """Correo de contacto opcional."""
        return self._email

    @email.setter
    def email(self, valor):
        """Valida el correo cuando se informa."""
        valor = Validar.sanitizar_texto(valor)
        if valor and not Validar.validar_email(valor):
            raise ValueError("El correo no tiene un formato válido.")
        self._email = valor

    @property
    def departamento(self):
        """Departamento asignado, o None mientras se prepara el objeto."""
        return self._departamento

    @property
    def registros(self):
        """Devuelve una vista que no permite agregar registros sin validación."""
        return tuple(self._registros)

    @property
    def proyectos(self):
        """Proyectos asignados."""
        return tuple(self._proyectos)

    def asignar_proyecto(self, proyecto):
        """Asigna un proyecto y mantiene la relación en ambos objetos."""
        from dominio.proyecto import Proyecto
        if not isinstance(proyecto, Proyecto):
            raise ValueError("Se esperaba un proyecto.")
        if proyecto not in self._proyectos:
            self._proyectos.append(proyecto)
            proyecto._empleados.append(self)

    def registrar_hora(self, registro):
        """Asocia una jornada con un proyecto previamente asignado."""
        from dominio.registro_tiempo import RegistroTiempo
        if not isinstance(registro, RegistroTiempo):
            raise ValueError("Se esperaba un registro de tiempo.")
        if registro.empleado is not self:
            raise ValueError("El registro pertenece a otro empleado.")
        if registro.proyecto not in self._proyectos:
            raise ValueError("Primero debes asignar al empleado al proyecto.")
        if registro.fecha < max(self.fecha_ingreso, registro.proyecto.fecha_inicio):
            raise ValueError("La jornada no puede ser anterior al empleado o al proyecto.")
        if registro in self._registros:
            raise ValueError("Ese registro ya está agregado.")
        horas_dia = 0
        for jornada in self._registros:
            if jornada.fecha == registro.fecha:
                horas_dia += jornada.horas
        if horas_dia + registro.horas > 24:
            raise ValueError("Un empleado no puede registrar más de 24 horas por día.")
        self._registros.append(registro)
        registro.proyecto._registros.append(registro)

    def total_horas(self):
        """Suma las horas registradas sin modificar los registros."""
        total = 0
        for registro in self._registros:
            total += registro.horas
        return total

    @abstractmethod
    def calcular_pago(self):
        """Cada tipo de contrato define su cálculo."""
        raise NotImplementedError

    def __repr__(self):
        """Muestra datos útiles sin exponer información de contacto."""
        return f"{type(self).__name__}(rut={self.rut!r}, nombre={self.nombre!r})"
