import os
import tempfile
import unittest

from password_vault.core import (
    derive_key,
    encrypt_data,
    decrypt_data,
    load_or_create_vault,
    save_vault,
)


class TestCore(unittest.TestCase):
    """Pruebas unitarias para el módulo core."""

    def test_encrypt_decrypt_roundtrip(self):
        """Los datos cifrados deben descifrarse correctamente con la contraseña correcta."""
        vault_data = {"entries": [{"title": "Prueba", "password": "1234"}]}
        salt = os.urandom(16)
        key = derive_key("clave_secreta", salt)
        encrypted = encrypt_data(vault_data, key, salt=salt)
        # Desencriptar con contraseña incorrecta debe fallar
        with self.assertRaises(ValueError):
            decrypt_data(encrypted, "otra")
        # Desencriptar con la contraseña correcta
        decrypted_data, derived_key = decrypt_data(encrypted, "clave_secreta")
        self.assertEqual(decrypted_data, vault_data)
        self.assertEqual(derived_key, key)

    def test_load_create_and_save(self):
        """Crear una nueva bóveda, modificar y guardar debe persistir los cambios."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_file = os.path.join(tmpdir, "vault_test.json")
            data, key = load_or_create_vault(vault_file, "clave")
            self.assertEqual(data, {"entries": []})
            # Segunda carga debe devolver la misma estructura
            data2, key2 = load_or_create_vault(vault_file, "clave")
            self.assertEqual(data2, data)
            # Modificar y guardar
            data2["entries"].append({"title": "Sitio", "password": "pass"})
            save_vault(vault_file, data2, key2)
            # Volver a cargar y verificar la modificación
            data3, _ = load_or_create_vault(vault_file, "clave")
            self.assertEqual(len(data3["entries"]), 1)


if __name__ == '__main__':
    unittest.main()
