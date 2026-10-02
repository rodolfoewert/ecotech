class Informe:
    """Un informe generado a partir de un proyecto."""

    def __init__(self, titulo, fecha_generacion):
        self.titulo = titulo
        self.fecha_generacion = fecha_generacion
        self.proyecto = None                # cardinalidad 0..1  ->  puede ser None

    def generar(self):
        """Hace algo: arma el contenido del informe."""
        ...