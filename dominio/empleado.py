from datetime import date

class Empleado:
    def __init__(self, rut: str, nombre: str, fecha_ingreso: date, sueldo_base: int):
        self.rut = rut
        self.nombre = nombre
        self.fecha_ingreso = fecha_ingreso
        self.sueldo_base = sueldo_base

    def __repr__(self):
        return f"Empleado(rut='{self.rut}', nombre='{self.nombre}', sueldo_base={self.sueldo_base})"