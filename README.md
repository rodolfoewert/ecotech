# EcoTech

Proyecto de Programación Orientada a Objeto Seguro TI3021.
Gestiona empleados, departamentos, proyectos y horas trabajadas usando Python y SQLite.

## Preparar y ejecutar en Windows

Desde la carpeta del repositorio:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python configurar.py
python main.py
```

El archivo `.env` debe tener `DB_MOTOR=sqlite` y `DB_NOMBRE=ecotech.db`.
`configurar.py` crea `.env` y genera una clave de cifrado si falta.
Si ya hay una clave, la conserva. No reemplaces esa clave si ya tienes contactos
cifrados: se necesita para volver a leerlos. `.env` y `.venv` quedan fuera de Git.
El esquema se crea al iniciar. Si la base es la versión anterior del proyecto,
se agregan las columnas nuevas sin borrar sus filas. Los contratos antiguos se
interpretan como empleados de planta con bono cero. Las descripciones antiguas
vacías se muestran como registros anteriores sin descripción.

En VS Code, usa **Python: Select Interpreter** y elige `.venv\Scripts\python.exe`.
Si aparece `No module named dotenv`, estás usando otro intérprete o faltan
las dependencias. Ejecuta `.venv\Scripts\python.exe -m pip install -r requirements.txt`
y usa ese mismo Python para correr el proyecto.

Para ver el ejemplo completo sin modificar la base de trabajo:

```powershell
python main.py --demo
```

## Qué se puede hacer

- Crear, consultar, modificar y eliminar empleados.
- Gestionar departamentos y proyectos con operaciones CRUD.
- Reasignar el departamento de un empleado.
- Asignar un empleado a varios proyectos y varios empleados a un proyecto.
- Registrar horas y consultar los totales y el pago bruto del empleado.

El menú pide un departamento al crear un empleado. El modelo y la base siguen
permitiendo empleados sin departamento para leer los datos de la versión de clase.
Las jornadas se leen junto al empleado para reconstruir sus proyectos y calcular
su pago con las horas guardadas. `ProyectoRepositorio` carga los datos propios del
proyecto; sus colecciones no representan un informe global de todos los empleados.

## Inicio de sesión

La primera ejecución pide crear un administrador con contraseña de al menos
10 caracteres. Después se inicia sesión con esa cuenta. El administrador puede
crear usuarios desde la opción 10. El rol `consulta` solo puede consultar empleados;
el rol `admin` puede gestionar datos y crear cuentas.

Las contraseñas no se guardan como texto. Se guarda un hash PBKDF2 con una sal
aleatoria por usuario. Dirección, teléfono y correo se cifran con Fernet antes de
escribirlos en SQLite y se recuperan al reconstruir el objeto. La clave está en
`.env`, separada de las filas de la base. Los datos de contacto de versiones
anteriores se cifran al inicializar el esquema.

Los permisos controlan el uso del menú. El acceso a los archivos locales y a la
clave también depende de los permisos de tu cuenta de Windows. RUT, nombre,
sueldos y horas permanecen sin cifrar; el cifrado implementado cubre los contactos.

## Clases y pagos

`Persona` conserva RUT y nombre, como en el laboratorio. `Empleado` hereda esos
datos y es abstracta. `EmpleadoPlanta` y `EmpleadoContratista` implementan
`calcular_pago()` de distinta forma:

- Planta: sueldo base más bono de sostenibilidad.
- Contratista: tarifa por hora multiplicada por sus horas registradas.

El sueldo base del contratista se conserva como referencia y no se suma al pago
por horas. Los resultados son pagos brutos de las jornadas cargadas; no son una
liquidación mensual ni incluyen impuestos o descuentos legales.

Los datos se validan antes de asignarlos. Los montos deben ser finitos y positivos
(el bono puede ser cero). Las fechas usan `date`. El RUT se conserva como texto,
con validación de formato, pero todavía sin comprobar el dígito verificador.
Correo, dirección y teléfono son opcionales; si se informan, se valida su formato.
Cada jornada admite hasta 24 horas y la suma diaria del empleado también tiene
ese límite, aunque trabaje en proyectos diferentes.

## Decisiones del laboratorio C08

| Decisión | Elección |
| --- | --- |
| Borrado | Físico con DELETE. El menú pide confirmación. |
| Hijos del empleado | Se borran jornadas y asignaciones con ON DELETE CASCADE. |
| Departamento con empleados | Se impide su eliminación. |
| Proyecto con jornadas o informes | Se impide su eliminación. |
| Identificadores | La base asigna los id numéricos; el RUT identifica al empleado. |

El dominio no ejecuta SQL. Los repositorios usan parámetros y reconstruyen
objetos con funciones de mapeo. El SQL dinámico de la migración utiliza únicamente
nombres y definiciones constantes, nunca entradas del usuario.
La conexión hace commit o rollback y siempre se cierra. Un RUT duplicado se
informa con `RutDuplicado`, una relación inválida con `RelacionInvalida` y un
problema de acceso a SQLite con `ErrorDeConexion`.

## Pruebas

```powershell
python -m unittest discover -s pruebas -v
```

Las pruebas usan archivos temporales. Comprueban CRUD, contratos, validaciones,
relaciones, inyección SQL, cascada, rollback, actualización de una base antigua,
inicio de sesión, permisos por rol y cifrado de contactos.

## Diferencias y pendientes del UML de la evaluación 1

Se conservó `Persona` del laboratorio para reutilizar nombre y RUT. Se usó RUT
en lugar del id_empleado numérico del UML. Los nombres `fecha_ingreso` y
`sueldo_base` equivalen a `fecha_inicio` y `salario_base` del informe anterior.
`Informe` es una extensión del material de clase y genera un resumen en memoria.
Las clases de dominio no crean filas: los métodos de creación de datos están en
los repositorios para mantener la separación de responsabilidades.

`GestorAutenticacion` implementa inicio de sesión, revisión de rol y acceso al
cifrado. La autenticación guarda un hash por cuenta en lugar del atributo global
`hash_sistema` del UML. Las propiedades validan cambios, mientras que el inicio
de sesión y los permisos se controlan por separado.
Las bases antiguas conservan sus tipos de columnas y restricciones originales:
la actualización agrega columnas y relaciones, pero no reconstruye las tablas.
También falta cerrar con el equipo la correspondencia final del UML y registrar
sus aportes reales para el informe y la defensa individual.

## Equipo

Repositorio de Rodolfo Ewert. Los integrantes, el líder de esta etapa y sus
aportes se completan con la información real del equipo antes de entregar.
