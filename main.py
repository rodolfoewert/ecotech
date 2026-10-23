"""Menú y demostración por consola de EcoTech."""

import argparse
import os
import tempfile
from datetime import date
from pathlib import Path

from dominio.departamento import Departamento
from dominio.empleado_planta import EmpleadoPlanta
from dominio.empleado_contratista import EmpleadoContratista
from dominio.excepciones import RutDuplicado, RelacionInvalida
from dominio.informe import Informe
from dominio.proyecto import Proyecto
from dominio.registro_tiempo import RegistroTiempo
from infraestructura.conexion import ErrorDeConexion
from infraestructura.departamento_repositorio import DepartamentoRepositorio
from infraestructura.empleado_repositorio import EmpleadoRepositorio
from infraestructura.esquema import inicializar_bd
from infraestructura.proyecto_repositorio import ProyectoRepositorio
from infraestructura.registro_tiempo_repositorio import RegistroTiempoRepositorio


def mostrar_empleado(empleado):
    """Muestra el contrato y los totales calculados a partir de sus jornadas."""
    departamento = empleado.departamento.nombre if empleado.departamento else "Sin asignar"
    print(f"{empleado.rut} | {empleado.nombre} | {type(empleado).__name__}")
    print(f"Departamento: {departamento} | Horas: {empleado.total_horas():g} | "
          f"Pago bruto: ${empleado.calcular_pago():,.0f}")


def pedir_empleado():
    """Recupera el empleado que se quiere gestionar."""
    empleado = EmpleadoRepositorio().obtener(input("RUT: ").strip().upper())
    if empleado is None:
        raise ValueError("No existe un empleado con ese RUT.")
    return empleado


def crear_empleado():
    """Pide datos, valida mediante las clases y guarda el contrato elegido."""
    tipo = input("Contrato (1 planta / 2 contratista): ").strip()
    if tipo not in ("1", "2"):
        raise ValueError("El contrato debe ser 1 o 2.")
    datos = dict(rut=input("RUT sin puntos: ").strip(), nombre=input("Nombre: "),
                 fecha_ingreso=date.fromisoformat(input("Ingreso (AAAA-MM-DD): ").strip()),
                 sueldo_base=float(input("Sueldo base de referencia: ")),
                 direccion=input("Dirección (opcional): "),
                 email=input("Correo (opcional): "), telefono=input("Teléfono (opcional): "))
    if tipo == "1":
        empleado = EmpleadoPlanta(**datos, bono_sostenibilidad=float(input("Bono: ")))
    else:
        empleado = EmpleadoContratista(**datos, tarifa_hora=float(input("Tarifa por hora: ")))
    departamento = DepartamentoRepositorio().obtener(int(input("ID del departamento: ")))
    if departamento is None:
        raise ValueError("Primero debes crear el departamento.")
    departamento.asignar_empleado(empleado)
    EmpleadoRepositorio().guardar(empleado)
    print("Empleado guardado.")


def listar_empleados():
    """Busca empleados y muestra sus totales reales."""
    empleados = EmpleadoRepositorio().listar(input("Filtrar nombre (Enter para todos): "))
    for empleado in empleados:
        mostrar_empleado(empleado)
    if not empleados:
        print("No hay empleados para ese filtro.")


def actualizar_empleado():
    """Permite cambiar los datos principales sin editar directamente la base."""
    empleado = pedir_empleado()
    empleado.nombre = input(f"Nombre [{empleado.nombre}]: ").strip() or empleado.nombre
    sueldo = input(f"Sueldo base [{empleado.sueldo_base}]: ").strip()
    if sueldo:
        empleado.sueldo_base = float(sueldo)
    if isinstance(empleado, EmpleadoPlanta):
        valor = input(f"Bono [{empleado.bono_sostenibilidad}]: ").strip()
        if valor:
            empleado.bono_sostenibilidad = float(valor)
    else:
        valor = input(f"Tarifa [{empleado.tarifa_hora}]: ").strip()
        if valor:
            empleado.tarifa_hora = float(valor)
    EmpleadoRepositorio().actualizar(empleado)
    print("Empleado actualizado.")


def eliminar_empleado():
    """Solicita confirmación antes de borrar un empleado y sus jornadas."""
    empleado = pedir_empleado()
    if input(f"¿Eliminar a {empleado.nombre} y sus jornadas? (s/n): ").strip().lower() == "s":
        EmpleadoRepositorio().eliminar(empleado.rut)
        print("Empleado eliminado.")


def gestionar_departamentos():
    """Ofrece el CRUD del segundo repositorio exigido en el laboratorio."""
    repo = DepartamentoRepositorio()
    for dep in repo.listar():
        print(f"{dep.id} | {dep.nombre} | Responsable: {dep.gerente}")
    opcion = input("1 Crear / 2 Modificar / 3 Eliminar / Enter Volver: ").strip()
    if not opcion:
        return
    if opcion == "1":
        dep = repo.guardar(Departamento(input("Nombre: "), gerente=input("Responsable: ")))
        print(f"Departamento guardado con ID {dep.id}.")
    elif opcion in ("2", "3"):
        dep = repo.obtener(int(input("ID: ")))
        if dep is None:
            raise ValueError("No existe el departamento.")
        if opcion == "2":
            dep.nombre = input("Nuevo nombre: ")
            dep.gerente = input("Responsable: ")
            repo.actualizar(dep)
            print("Departamento actualizado.")
        elif input("¿Confirmas eliminarlo? (s/n): ").strip().lower() == "s":
            repo.eliminar(dep.id)
            print("Departamento eliminado.")
    else:
        raise ValueError("Opción inválida.")


def gestionar_proyectos():
    """Crea, consulta, modifica y elimina los datos propios de los proyectos."""
    repo = ProyectoRepositorio()
    for proyecto in repo.listar():
        print(f"{proyecto.id} | {proyecto.nombre} | {proyecto.fecha_inicio}")
    opcion = input("1 Crear / 2 Modificar / 3 Eliminar / Enter Volver: ").strip()
    if not opcion:
        return
    if opcion == "1":
        proyecto = Proyecto(None, input("Nombre: "),
            date.fromisoformat(input("Inicio (AAAA-MM-DD): ").strip()), input("Descripción: "))
        repo.guardar(proyecto)
        print(f"Proyecto guardado con ID {proyecto.id}.")
    elif opcion in ("2", "3"):
        proyecto = repo.obtener(int(input("ID: ")))
        if proyecto is None:
            raise ValueError("No existe el proyecto.")
        if opcion == "2":
            proyecto.nombre = input("Nuevo nombre: ")
            proyecto.descripcion = input("Descripción: ")
            repo.actualizar(proyecto)
            print("Proyecto actualizado.")
        elif input("¿Confirmas eliminarlo? (s/n): ").strip().lower() == "s":
            repo.eliminar(proyecto.id)
            print("Proyecto eliminado.")
    else:
        raise ValueError("Opción inválida.")


def asignar_proyecto():
    """Asigna un empleado ya guardado a un proyecto existente."""
    empleado = pedir_empleado()
    proyecto = ProyectoRepositorio().obtener(int(input("ID del proyecto: ")))
    if proyecto is None:
        raise ValueError("No existe el proyecto.")
    nuevo = EmpleadoRepositorio().asignar_proyecto(empleado, proyecto)
    print("Asignación guardada." if nuevo else "El empleado ya estaba asignado.")


def registrar_horas():
    """Guarda una jornada de un empleado en uno de sus proyectos asignados."""
    empleado = pedir_empleado()
    for proyecto in empleado.proyectos:
        print(f"{proyecto.id} | {proyecto.nombre}")
    identificador = int(input("ID del proyecto asignado: "))
    proyecto = next((p for p in empleado.proyectos if p.id == identificador), None)
    if proyecto is None:
        raise ValueError("El empleado no está asignado a ese proyecto.")
    registro = RegistroTiempo(date.fromisoformat(input("Fecha (AAAA-MM-DD): ").strip()),
        float(input("Horas: ")), input("Actividad: "), empleado, proyecto)
    registro.ingresar_registro()
    RegistroTiempoRepositorio().guardar(registro)
    print("Jornada guardada.")


def cambiar_departamento():
    """Reasigna al empleado a una única área."""
    empleado = pedir_empleado()
    departamento = DepartamentoRepositorio().obtener(int(input("ID del departamento: ")))
    if departamento is None:
        raise ValueError("No existe el departamento.")
    departamento.asignar_empleado(empleado)
    EmpleadoRepositorio().actualizar(empleado)
    print("Departamento actualizado.")


def menu():
    """Mantiene el menú disponible ante entradas inválidas o errores esperados."""
    inicializar_bd()
    acciones = {"1": crear_empleado, "2": listar_empleados, "3": actualizar_empleado,
                "4": eliminar_empleado, "5": gestionar_departamentos,
                "6": gestionar_proyectos, "7": asignar_proyecto,
                "8": registrar_horas, "9": cambiar_departamento}
    while True:
        print("\nEcoTech\n1 Crear empleado\n2 Consultar empleados\n3 Actualizar empleado"
              "\n4 Eliminar empleado\n5 Departamentos\n6 Proyectos\n7 Asignar proyecto"
              "\n8 Registrar horas\n9 Cambiar departamento\n0 Salir")
        opcion = input("Opción: ").strip()
        if opcion == "0":
            return
        accion = acciones.get(opcion)
        if accion is None:
            print("Elige una opción de la lista.")
            continue
        try:
            accion()
        except (ValueError, ErrorDeConexion) as error:
            print(f"No se pudo completar la operación: {error}")


def _demostrar():
    """Ejecuta un ciclo comprobable usando todos los objetos centrales."""
    inicializar_bd()
    departamentos = DepartamentoRepositorio()
    empleados = EmpleadoRepositorio()
    proyectos = ProyectoRepositorio()
    departamento = departamentos.guardar(Departamento("Tecnología", gerente="Ana"))
    proyecto = proyectos.guardar(Proyecto(None, "SolarEco", date(2026, 1, 1), "Energía solar"))
    ana = EmpleadoPlanta("12345678-9", "Ana", date(2024, 1, 1), 950000, 50000)
    luis = EmpleadoContratista("11111111-1", "Luis", date(2024, 1, 1), 950000, 10000)
    for empleado in (ana, luis):
        departamento.asignar_empleado(empleado)
        empleados.guardar(empleado)
        empleados.asignar_proyecto(empleado, proyecto)
        registro = RegistroTiempo(date(2026, 1, 2), 3, "Desarrollo", empleado, proyecto)
        registro.ingresar_registro()
        RegistroTiempoRepositorio().guardar(registro)
        mostrar_empleado(empleados.obtener(empleado.rut))
    ana.sueldo_base = 1000000
    empleados.actualizar(ana)
    departamento.nombre = "Desarrollo sostenible"
    departamentos.actualizar(departamento)
    proyecto.descripcion = "Prueba del CRUD de proyectos"
    proyectos.actualizar(proyecto)
    print(Informe("Resumen", date(2026, 1, 2), proyecto).generar())
    for repositorio in (empleados, departamentos, proyectos):
        resultado = repositorio.listar("' OR '1'='1")
        if resultado:
            raise RuntimeError("La prueba de inyección devolvió datos inesperados.")
    print("Consultas parametrizadas: prueba superada.")
    for empleado in (ana, luis):
        empleados.eliminar(empleado.rut)
    proyectos.eliminar(proyecto.id)
    departamentos.eliminar(departamento.id)
    print("CRUD, contratos y registros: demostración terminada.")


def ejecutar_laboratorio():
    """La demostración usa una base temporal y no toca los datos de trabajo."""
    anteriores = {clave: os.environ.get(clave) for clave in ("DB_NOMBRE", "DB_MOTOR")}
    try:
        with tempfile.TemporaryDirectory() as carpeta:
            os.environ["DB_NOMBRE"] = str(Path(carpeta) / "demo.db")
            os.environ["DB_MOTOR"] = "sqlite"
            _demostrar()
    finally:
        for clave, valor in anteriores.items():
            if valor is None:
                os.environ.pop(clave, None)
            else:
                os.environ[clave] = valor


def main():
    """Inicia el menú o una demostración independiente."""
    argumentos = argparse.ArgumentParser(description="Sistema EcoTech por consola")
    argumentos.add_argument("--demo", action="store_true", help="Demostración con datos temporales")
    opciones = argumentos.parse_args()
    try:
        if opciones.demo:
            ejecutar_laboratorio()
        else:
            menu()
    except (ValueError, ErrorDeConexion) as error:
        print(f"No se pudo iniciar EcoTech: {error}")
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nSesión finalizada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
