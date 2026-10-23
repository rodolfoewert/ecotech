import math
import re
from datetime import date


class ValidadorEntradas:
    """Revisa los datos antes de modificar un objeto."""

    @staticmethod
    def sanitizar_texto(entrada):
        """Quita espacios exteriores; el SQL se protege con parámetros, no aquí."""
        if not isinstance(entrada, str):
            raise ValueError("Se esperaba un texto.")
        return entrada.strip()

    @staticmethod
    def texto(valor, campo):
        """Exige un texto no vacío."""
        valor = ValidadorEntradas.sanitizar_texto(valor)
        if not valor:
            raise ValueError(f"{campo} no puede estar vacío.")
        return valor

    @staticmethod
    def numero(valor, campo, minimo=0, estricto=False):
        """Rechaza negativos, booleanos, infinitos y valores que no son números."""
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError(f"{campo} debe ser un número.")
        if not math.isfinite(valor) or valor < minimo or (estricto and valor == minimo):
            raise ValueError(f"{campo} está fuera del rango permitido.")
        return valor

    @staticmethod
    def fecha(valor):
        """Las clases usan date; la persistencia convierte desde y hacia ISO."""
        if type(valor) is not date:
            raise ValueError("La fecha debe ser un objeto date.")
        return valor

    @staticmethod
    def validar_email(email):
        """Valida la estructura básica de un correo, sin comprobar su existencia."""
        return isinstance(email, str) and bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email))

    @staticmethod
    def validar_telefono(telefono):
        """Acepta entre 8 y 15 dígitos y un prefijo + opcional."""
        return isinstance(telefono, str) and bool(re.fullmatch(r"\+?[0-9]{8,15}", telefono))

    @staticmethod
    def rut(valor):
        """Comprueba el formato; no valida el dígito verificador en esta etapa."""
        valor = ValidadorEntradas.texto(valor, "RUT").upper()
        if not re.fullmatch(r"[0-9]{7,8}-[0-9K]", valor):
            raise ValueError("El RUT debe tener un formato como 12345678-9.")
        return valor
