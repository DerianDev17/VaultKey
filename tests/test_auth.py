"""Pruebas unitarias para el módulo de autenticación.

Este conjunto de pruebas verifica que la creación de usuarios y la
autenticación funcionen correctamente, así como la correcta gestión
de errores al intentar registrar usuarios duplicados.  Se utilizan
archivos temporales para garantizar que las pruebas no interfieran
con la base de datos de usuarios en un entorno real.
"""

import os
import tempfile
import unittest

from password_vault.auth import create_user, authenticate


class TestAuth(unittest.TestCase):
    """Pruebas para las funciones de creación y autenticación de usuarios."""

    def test_create_and_authenticate_user(self) -> None:
        """Comprueba que se puede crear un usuario y autenticarlo."""
        # Crear un archivo temporal para la base de datos
        fd, db_path = tempfile.mkstemp()
        os.close(fd)  # Cerrar el descriptor; usaremos solo la ruta
        try:
            # Crear el usuario
            create_user("alice", "contraseña123", db_path)
            # Autenticación correcta
            self.assertTrue(authenticate("alice", "contraseña123", db_path))
            # Contraseña incorrecta
            self.assertFalse(authenticate("alice", "otra", db_path))
            # Usuario inexistente
            self.assertFalse(authenticate("bob", "contraseña", db_path))
            # Intentar crear un usuario que ya existe genera una excepción
            with self.assertRaises(ValueError):
                create_user("alice", "contraseña123", db_path)
        finally:
            # Eliminar el archivo temporal
            if os.path.exists(db_path):
                os.remove(db_path)


if __name__ == '__main__':
    unittest.main()