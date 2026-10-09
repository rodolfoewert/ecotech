# EcoTech - De UML a Python (Laboratorio C05)

Sistema base de gestión de personal, departamentos y registros de tiempo para EcoTech.

# Rodolfo Ewert

## Cómo ejecutar el proyecto
1. Clonar el repositorio.
2. (Opcional) Activar el entorno virtual.
3. Ejecutar el punto de entrada:
   ```bash
   python main.py

## Decisiones de Diseño (Laboratorio C08)

| Decisión | Elección | Justificación |
| :--- | :--- | :--- |
| **¿Se borra de verdad?** | DELETE real (borrado físico) | Se elimina el registro de la base de datos para pruebas limpias del ciclo CRUD. |
| **¿Qué pasa con los hijos?** | Cascada (`ON DELETE CASCADE`) | Configurado en el esquema para que los registros de tiempo se eliminen si se borra el empleado. |
| **¿Quién asigna el id?** | La base (autoincremento) | Las tablas dependientes y secundarias usan `INTEGER PRIMARY KEY AUTOINCREMENT`. |