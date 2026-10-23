import hashlib
import hmac
import secrets

from seguridad.cifrado import cifrar


class GestorAutenticacion:
    """Valida el acceso y los permisos de la sesión de consola."""

    def __init__(self, repositorio):
        """Recibe el repositorio para no mezclar autenticación con SQL."""
        self.repositorio = repositorio
        self.usuario_actual = None

    def registrar_usuario(self, nombre, contrasenia, rol):
        """El primer usuario es administrador; después solo un admin crea cuentas."""
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre de usuario es obligatorio.")
        nombre = nombre.strip()
        if len(nombre) > 50:
            raise ValueError("El nombre de usuario admite hasta 50 caracteres.")
        if not isinstance(contrasenia, str) or len(contrasenia) < 10:
            raise ValueError("La contraseña debe tener al menos 10 caracteres.")
        if rol not in ("admin", "consulta"):
            raise ValueError("El rol debe ser admin o consulta.")
        if self.repositorio.hay_usuarios():
            if not self.verificar_rol(self.usuario_actual, "usuarios"):
                raise ValueError("Solo un administrador puede crear usuarios.")
        elif rol != "admin":
            raise ValueError("El primer usuario debe ser administrador.")
        sal = secrets.token_bytes(16)
        hash_clave = hashlib.pbkdf2_hmac("sha256", contrasenia.encode("utf-8"), sal, 600000)
        self.repositorio.guardar(nombre, sal.hex(), hash_clave.hex(), rol)

    def iniciar_sesion(self, usuario, contrasenia):
        """Compara hashes y borra la sesión anterior si falla el acceso."""
        self.usuario_actual = None
        if not isinstance(usuario, str) or not isinstance(contrasenia, str):
            return False
        datos = self.repositorio.obtener(usuario.strip())
        if datos is None:
            return False
        sal = bytes.fromhex(datos[1])
        calculado = hashlib.pbkdf2_hmac("sha256", contrasenia.encode("utf-8"), sal, 600000)
        if not hmac.compare_digest(calculado.hex(), datos[2]):
            return False
        self.usuario_actual = datos[0]
        return True

    def verificar_rol(self, usuario, modulo):
        """Revisa los permisos de quien inició sesión, no de otro nombre recibido."""
        if usuario is None or usuario != self.usuario_actual:
            return False
        datos = self.repositorio.obtener(usuario)
        if datos is None:
            return False
        if modulo == "consulta":
            return datos[3] in ("admin", "consulta")
        if modulo in ("administrar", "usuarios"):
            return datos[3] == "admin"
        return False

    def cifrar_datos_sensibles(self, datos):
        """Usa el mismo cifrado de los datos de contacto."""
        return cifrar(datos)
