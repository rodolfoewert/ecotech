import os

from cryptography.fernet import Fernet, InvalidToken


class ErrorDeCifrado(ValueError):
    """La clave no permite proteger o recuperar los datos."""


def obtener_cifrador():
    """Lee la clave local, que no se sube a Git."""
    clave = os.environ.get("CLAVE_CIFRADO", "")
    try:
        return Fernet(clave.encode("ascii"))
    except (ValueError, UnicodeError) as error:
        raise ErrorDeCifrado("Falta una CLAVE_CIFRADO válida en .env.") from error


def cifrar(texto):
    """Protege un dato de contacto antes de guardarlo."""
    if not texto:
        return ""
    token = obtener_cifrador().encrypt(texto.encode("utf-8"))
    return "fernet:" + token.decode("ascii")


def descifrar(texto):
    """Recupera un dato cifrado y detecta claves incorrectas o datos alterados."""
    if not texto:
        return ""
    if not texto.startswith("fernet:"):
        raise ErrorDeCifrado("Hay datos antiguos sin cifrar. Inicializa el esquema.")
    try:
        contenido = texto[len("fernet:"):].encode("ascii")
        return obtener_cifrador().decrypt(contenido).decode("utf-8")
    except (InvalidToken, UnicodeError) as error:
        raise ErrorDeCifrado("No se pueden recuperar los datos. Revisa la clave de cifrado.") from error
