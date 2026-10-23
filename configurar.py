from pathlib import Path

from cryptography.fernet import Fernet


def preparar_configuracion():
    """Crea la configuración local y genera la clave de cifrado si falta."""
    carpeta = Path(__file__).resolve().parent
    ruta = carpeta / ".env"
    if ruta.exists():
        texto = ruta.read_text(encoding="utf-8")
    else:
        texto = (carpeta / ".env.example").read_text(encoding="utf-8")
    lineas = texto.splitlines()
    tiene_clave = False
    for linea in lineas:
        if linea.startswith("CLAVE_CIFRADO=") and linea.split("=", 1)[1].strip():
            tiene_clave = True
    if not tiene_clave:
        clave = Fernet.generate_key().decode("ascii")
        nuevas = []
        for linea in lineas:
            if not linea.startswith("CLAVE_CIFRADO="):
                nuevas.append(linea)
        nuevas.append("CLAVE_CIFRADO=" + clave)
        lineas = nuevas
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("Configuración local lista. La clave queda guardada en .env.")


if __name__ == "__main__":
    preparar_configuracion()
