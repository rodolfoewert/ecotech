class Proyecto:
    """Un proyecto de EcoTech. Recibe registros de tiempo de los empleados."""

    def __init__(self, id, nombre, fecha_inicio):
        self.id = id
        self.nombre = nombre
        self.fecha_inicio = fecha_inicio
        self.registros = []                 # cardinalidad 1..*  ->  lista
        self.informes = []                  # cardinalidad 0..*  ->  lista

    def agregar_registro(self, registro):
        """Hace algo: agrega un registro de tiempo al proyecto."""
        ...

    def total_horas(self):
        """Calcula y devuelve las horas del proyecto: no cambia nada."""
        ...