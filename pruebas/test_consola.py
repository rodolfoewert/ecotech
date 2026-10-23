"""Comprueba que el menú se recupere y que la demo no cambie la configuración."""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from main import ejecutar_laboratorio, menu


class PruebasConsola(unittest.TestCase):
    """Ejercita entradas de usuario y el ejemplo completo."""

    def test_menu_se_recupera_de_opcion_y_numero_invalidos(self):
        with tempfile.TemporaryDirectory() as carpeta:
            with patch.dict(os.environ, {"DB_NOMBRE": str(Path(carpeta) / "menu.db"),
                                         "DB_MOTOR": "sqlite"}):
                salida = io.StringIO()
                with redirect_stdout(salida):
                    with patch("builtins.input", side_effect=["invalida", "5", "3", "abc", "0"]):
                        menu()
                self.assertIn("Elige una opción", salida.getvalue())
                self.assertIn("No se pudo completar la operación", salida.getvalue())

    def test_demo_no_toca_base_de_trabajo_y_restaura_entorno(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "trabajo.db"
            ruta.write_bytes(b"datos que la demo no debe modificar")
            with patch.dict(os.environ, {"DB_NOMBRE": str(ruta), "DB_MOTOR": "sqlite"}):
                salida = io.StringIO()
                with redirect_stdout(salida):
                    ejecutar_laboratorio()
                self.assertEqual(os.environ["DB_NOMBRE"], str(ruta))
                self.assertEqual(ruta.read_bytes(), b"datos que la demo no debe modificar")
                self.assertIn("Horas registradas: 6", salida.getvalue())
                self.assertIn("prueba superada", salida.getvalue())
