import sqlite3

from infraestructura.conexion import obtener_conexion


class UsuarioRepositorio:
    """Guarda usuarios y hashes, nunca las contraseñas originales."""

    def obtener(self, nombre):
        """Devuelve los datos de acceso o None."""
        with obtener_conexion() as conn:
            fila = conn.execute("SELECT nombre, sal, hash_clave, rol FROM usuario "
                                "WHERE nombre = ?", (nombre,)).fetchone()
        return fila

    def hay_usuarios(self):
        """Permite preparar el primer administrador."""
        with obtener_conexion() as conn:
            return conn.execute("SELECT 1 FROM usuario LIMIT 1").fetchone() is not None

    def guardar(self, nombre, sal, hash_clave, rol):
        """Guarda una cuenta nueva con su rol."""
        try:
            with obtener_conexion() as conn:
                conn.execute("INSERT INTO usuario(nombre, sal, hash_clave, rol) "
                             "VALUES (?, ?, ?, ?)", (nombre, sal, hash_clave, rol))
        except sqlite3.IntegrityError as error:
            raise ValueError("El usuario ya existe o su rol es inválido.") from error
