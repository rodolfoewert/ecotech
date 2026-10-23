"""Resumen sencillo de las horas de un proyecto."""

from dominio.validador_entradas import ValidadorEntradas as Validar


class Informe:
    """Extensión del laboratorio para resumir el trabajo registrado."""

    def __init__(self, titulo, fecha_generacion, proyecto=None):
        """Prepara el informe y su proyecto opcional."""
        self.titulo = Validar.texto(titulo, "Título")
        self.fecha_generacion = Validar.fecha(fecha_generacion)
        self.proyecto = proyecto

    def generar(self):
        """Devuelve un texto sin escribir en la base de datos."""
        from dominio.proyecto import Proyecto
        if not isinstance(self.proyecto, Proyecto):
            raise ValueError("Debes asociar un proyecto antes de generar el informe.")
        return (f"{self.titulo} - {self.fecha_generacion.isoformat()}\n"
                f"Proyecto: {self.proyecto.nombre}\n"
                f"Horas registradas: {self.proyecto.total_horas():g}")
