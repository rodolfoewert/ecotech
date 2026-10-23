# EcoTech - De UML a Python (Laboratorio C05)

Sistema base de gestión de personal, departamentos y registros de tiempo para EcoTech.

# Rodolfo Ewert

## Cómo ejecutar el proyecto
1. Clonar el repositorio.
2. Crear y activar el entorno virtual: `python -m venv .venv` y `.venv\Scripts\activate`.
3. Instalar dependencias: `python -m pip install -r requirements.txt`.
4. Copiar `.env.example` a `.env` (en PowerShell: `Copy-Item .env.example .env`).
5. Ejecutar el punto de entrada:
   ```bash
   python main.py
   ```

## Decisiones de Diseño (Laboratorio C08)

| Decisión | Elección | Justificación |
| :--- | :--- | :--- |
| **¿Se borra de verdad?** | DELETE real (borrado físico) | Se elimina el registro de la base de datos para pruebas limpias del ciclo CRUD. |
| **¿Qué pasa con los hijos?** | Cascada (`ON DELETE CASCADE`) | Configurado en el esquema para que los registros de tiempo se eliminen si se borra el empleado. |
| **¿Quién asigna el id?** | La base (autoincremento) | Las tablas dependientes y secundarias usan `INTEGER PRIMARY KEY AUTOINCREMENT`. |
## Pruebas

Ejecutar `python -m unittest discover -s pruebas -v`. Las pruebas usan bases
temporales y no modifican la base de trabajo.

La conexión confirma las operaciones juntas y hace rollback ante un fallo.
Un RUT duplicado se informa como `RutDuplicado`; un departamento con empleados
no se puede eliminar y se informa como `RelacionInvalida`.
