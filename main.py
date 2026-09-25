from dominio.departamento import Departamento
from dominio.empleado import Empleado
from dominio.registro_tiempo import RegistroTiempo


def main():
    dep = Departamento("Operaciones")
    ana = Empleado("12345678-9", "Ana Rojas", "2024-03-01", 950000)

    dep.agregar_empleado(ana)

    reg1 = RegistroTiempo("2026-09-21", 4.5, "Desarrollo de módulos")
    reg2 = RegistroTiempo("2026-09-22", 3.5, "Revisión de código")

    ana.registrar_hora(reg1)
    ana.registrar_hora(reg2)

    print("Departamento:", dep.nombre)
    print("Empleado:", ana.nombre, "| RUT:", ana.rut)
    print("Departamento asignado:", ana.departamento.nombre)
    print("Total de horas registradas:", ana.total_horas())


if __name__ == "__main__":
    main()