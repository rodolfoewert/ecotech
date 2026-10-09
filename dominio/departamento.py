class Departamento:
    def __init__(self, nombre: str, id: int = None):
        self.id = id
        self.nombre = nombre

    def __repr__(self):
        return f"Departamento(id={self.id}, nombre='{self.nombre}')"