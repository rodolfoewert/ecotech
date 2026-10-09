from datetime import date
import os
from dominio.empleado import Empleado
from dominio.departamento import Departamento
from infraestructura.conexion import obtener_conexion
from infraestructura.empleado_repositorio import EmpleadoRepositorio
from infraestructura.departamento_repositorio import DepartamentoRepositorio

def inicializar_bd():
    ruta_esquema = os.path.join(os.path.dirname(__file__), "db", "01_esquema.sql")
    with open(ruta_esquema, "r", encoding="utf-8") as f:
        script_sql = f.read()
    with obtener_conexion() as conn:
        conn.executescript(script_sql)

def ejecutar_laboratorio():
    inicializar_bd()

    print("========================================")
    print("       ENTIDAD 1: EMPLEADO")
    print("========================================")
    repo_emp = EmpleadoRepositorio()

    print("--- 1. CREAR ---")
    ana = Empleado("12345678-9", "Ana Rojas", date(2024, 3, 1), 950_000)
    repo_emp.guardar(ana)
    print(f"Guardado: {ana}")

    print("\n--- 2. LEER ---")
    print(f"Obtenido: {repo_emp.obtener('12345678-9')}")
    print(f"Listar: {len(repo_emp.listar())} registros")

    print("\n--- 3. ACTUALIZAR ---")
    ana.sueldo_base = 1_050_000
    repo_emp.actualizar(ana)
    print(f"Sueldo actualizado: {repo_emp.obtener('12345678-9').sueldo_base}")

    print("\n--- 4. PRUEBA DE INYECCIÓN SQL ---")
    payload = "' OR '1'='1"
    res_emp = repo_emp.listar(nombre_contiene=payload)
    print(f"Resultado con payload: {res_emp}")
    print("✔ SUPERADA: Parametrización blindada" if len(res_emp) == 0 else "✘ FALLIDA")

    print("\n--- 5. ELIMINAR ---")
    repo_emp.eliminar("12345678-9")
    print(f"Comprobación eliminación: {repo_emp.obtener('12345678-9')}")

    print("\n========================================")
    print("       ENTIDAD 2: DEPARTAMENTO")
    print("========================================")
    repo_dep = DepartamentoRepositorio()

    print("--- 1. CREAR ---")
    depto = Departamento("Tecnología")
    repo_dep.guardar(depto)
    print(f"Guardado con ID autoincremental: {depto}")

    print("\n--- 2. LEER ---")
    print(f"Obtenido por ID: {repo_dep.obtener(depto.id)}")
    print(f"Total departamentos: {len(repo_dep.listar())}")

    print("\n--- 3. ACTUALIZAR ---")
    depto.nombre = "I+D e Innovación"
    repo_dep.actualizar(depto)
    print(f"Nombre actualizado: {repo_dep.obtener(depto.id).nombre}")

    print("\n--- 4. PRUEBA DE INYECCIÓN SQL ---")
    res_dep = repo_dep.listar(nombre_contiene=payload)
    print(f"Resultado con payload: {res_dep}")
    print("✔ SUPERADA: Parametrización blindada" if len(res_dep) == 0 else "✘ FALLIDA")

    print("\n--- 5. ELIMINAR ---")
    repo_dep.eliminar(depto.id)
    print(f"Comprobación eliminación: {repo_dep.obtener(depto.id)}")

if __name__ == "__main__":
    ejecutar_laboratorio()