import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from unittest.mock import patch

from cryptography.fernet import Fernet

from configurar import preparar_configuracion
from dominio.empleado_planta import EmpleadoPlanta
from infraestructura.conexion import obtener_conexion
from infraestructura.empleado_repositorio import EmpleadoRepositorio
from infraestructura.esquema import inicializar_bd
from infraestructura.usuario_repositorio import UsuarioRepositorio
from main import iniciar_acceso, menu
from seguridad.cifrado import ErrorDeCifrado, cifrar, descifrar
from seguridad.gestor_autenticacion import GestorAutenticacion


class PruebasSeguridad(unittest.TestCase):
    """Comprueba acceso, permisos y protección de los contactos."""

    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.carpeta = Path(temporal.name)
        entorno = patch.dict(os.environ, {
            "DB_NOMBRE": str(self.carpeta / "seguridad.db"), "DB_MOTOR": "sqlite",
            "CLAVE_CIFRADO": Fernet.generate_key().decode("ascii")
        })
        entorno.start()
        self.addCleanup(entorno.stop)
        inicializar_bd()
        self.repo = UsuarioRepositorio()
        self.gestor = GestorAutenticacion(self.repo)

    def registrar_admin(self):
        self.gestor.registrar_usuario("rodolfo", "clave de prueba 123", "admin")
        self.assertTrue(self.gestor.iniciar_sesion("rodolfo", "clave de prueba 123"))

    def test_hash_con_sal_y_acceso_fallido_borra_sesion(self):
        self.registrar_admin()
        self.gestor.registrar_usuario("lector", "clave de prueba 123", "consulta")
        admin = self.repo.obtener("rodolfo")
        lector = self.repo.obtener("lector")
        self.assertNotEqual(admin[1], lector[1])
        self.assertNotEqual(admin[2], lector[2])
        self.assertNotIn("clave de prueba 123", str(admin))
        self.assertFalse(self.gestor.iniciar_sesion("rodolfo", "incorrecta"))
        self.assertIsNone(self.gestor.usuario_actual)
        self.assertFalse(self.gestor.verificar_rol("rodolfo", "administrar"))

    def test_rol_consulta_no_modifica_ni_crea_usuarios(self):
        self.registrar_admin()
        self.gestor.registrar_usuario("lector", "otra clave 123", "consulta")
        self.assertTrue(self.gestor.iniciar_sesion("lector", "otra clave 123"))
        self.assertTrue(self.gestor.verificar_rol("lector", "consulta"))
        self.assertFalse(self.gestor.verificar_rol("lector", "administrar"))
        self.assertFalse(self.gestor.verificar_rol("rodolfo", "administrar"))
        with self.assertRaises(ValueError):
            self.gestor.registrar_usuario("nuevo", "una clave larga 123", "admin")
        salida = io.StringIO()
        with redirect_stdout(salida):
            with patch("builtins.input", side_effect=["1", "10", "0"]):
                menu(self.gestor)
        self.assertEqual(salida.getvalue().count("no tiene permiso"), 2)
        with obtener_conexion() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM empleado").fetchone()[0], 0)

    def test_credenciales_y_roles_invalidos(self):
        with self.assertRaises(ValueError):
            self.gestor.registrar_usuario("lector", "clave extensa 123", "consulta")
        with self.assertRaises(ValueError):
            self.gestor.registrar_usuario("admin", "corta", "admin")
        self.registrar_admin()
        with self.assertRaises(ValueError):
            self.gestor.registrar_usuario("otro", "clave extensa 123", "invalido")
        self.assertFalse(self.gestor.iniciar_sesion("' OR '1'='1", "clave de prueba 123"))

    def test_contactos_se_guardan_cifrados_y_se_recuperan(self):
        empleado = EmpleadoPlanta("12345678-9", "Ana", date(2024, 1, 1), 900000,
            direccion="Calle de prueba 123", telefono="+56912345678", email="ana@ejemplo.cl")
        repo = EmpleadoRepositorio()
        repo.guardar(empleado)
        with obtener_conexion() as conn:
            fila = conn.execute("SELECT direccion, telefono, email FROM empleado").fetchone()
        for campo, original in zip(fila, [empleado.direccion, empleado.telefono, empleado.email]):
            self.assertTrue(campo.startswith("fernet:"))
            self.assertNotIn(original, campo)
        leido = repo.obtener(empleado.rut)
        self.assertEqual(leido.direccion, empleado.direccion)
        self.assertEqual(leido.telefono, empleado.telefono)
        self.assertEqual(leido.email, empleado.email)
        empleado.email = "nuevo@ejemplo.cl"
        repo.actualizar(empleado)
        self.assertEqual(repo.obtener(empleado.rut).email, "nuevo@ejemplo.cl")

    def test_clave_incorrecta_no_devuelve_datos_ni_sobrescribe(self):
        protegido = cifrar("dato de prueba")
        with patch.dict(os.environ, {"CLAVE_CIFRADO": Fernet.generate_key().decode("ascii")}):
            with self.assertRaises(ErrorDeCifrado):
                descifrar(protegido)
        with patch.dict(os.environ, {"CLAVE_CIFRADO": ""}):
            with self.assertRaises(ErrorDeCifrado):
                cifrar("dato")
        self.assertEqual(descifrar(protegido), "dato de prueba")

    def test_migracion_cifra_contactos_antiguos_sin_perderlos(self):
        with obtener_conexion() as conn:
            conn.execute("INSERT INTO persona VALUES (?, ?)", ("12345678-9", "Ana"))
            conn.execute("""INSERT INTO empleado(rut, fecha_ingreso, sueldo_base, email)
                         VALUES (?, ?, ?, ?)""", ("12345678-9", "2024-01-01", 900000,
                                                  "ana@ejemplo.cl"))
        inicializar_bd()
        inicializar_bd()
        self.assertEqual(EmpleadoRepositorio().obtener("12345678-9").email, "ana@ejemplo.cl")
        with obtener_conexion() as conn:
            self.assertTrue(conn.execute("SELECT email FROM empleado").fetchone()[0].startswith(
                "fernet:"))

    def test_configuracion_conserva_la_clave_al_repetirse(self):
        (self.carpeta / ".env.example").write_text(
            "DB_NOMBRE=ecotech.db\nCLAVE_CIFRADO=\n", encoding="utf-8")
        with patch("configurar.__file__", str(self.carpeta / "configurar.py")):
            with redirect_stdout(io.StringIO()):
                preparar_configuracion()
                primera = (self.carpeta / ".env").read_bytes()
                preparar_configuracion()
                self.assertEqual((self.carpeta / ".env").read_bytes(), primera)

    def test_primera_ejecucion_crea_admin_y_pide_iniciar_sesion(self):
        with redirect_stdout(io.StringIO()):
            with patch("builtins.input", side_effect=["admin", "admin"]):
                with patch("main.getpass", side_effect=["clave de prueba 123"] * 3):
                    gestor = iniciar_acceso()
        self.assertEqual(gestor.usuario_actual, "admin")
        self.assertTrue(gestor.verificar_rol("admin", "administrar"))

    def test_tres_intentos_fallidos_terminan_el_acceso(self):
        self.registrar_admin()
        with redirect_stdout(io.StringIO()):
            with patch("builtins.input", return_value="inexistente"):
                with patch("main.getpass", return_value="incorrecta"):
                    with self.assertRaises(ValueError):
                        iniciar_acceso()
