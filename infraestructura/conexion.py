import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Iterator
from dotenv import load_dotenv

# Ruta absoluta al archivo .env ubicado en la raíz del proyecto
RUTA_RAIZ = Path(__file__).resolve().parent.parent
RUTA_ENV = RUTA_RAIZ / ".env"
load_dotenv(dotenv_path=RUTA_ENV)

class ErrorDeConexion(Exception):
    """La base de datos no está disponible."""

@contextmanager
def obtener_conexion() -> Iterator[sqlite3.Connection]:
    # Lee DB_NOMBRE del entorno; si no existe, toma 'ecotech.db' en la raíz como respaldo
    nombre_db = os.environ.get("DB_NOMBRE") or "ecotech.db"
    ruta_db = RUTA_RAIZ / nombre_db

    conn = None
    try:
        conn = sqlite3.connect(ruta_db)
        conn.execute("PRAGMA foreign_keys = ON")   # SQLite las ignora si no se activan
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise ErrorDeConexion(f"No se pudo operar sobre la base: {e}") from e
    finally:
        if conn:
            conn.close()