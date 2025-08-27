import os
import tempfile
import time
import unittest

from password_vault.cloud import LocalCloudSync


class TestCloud(unittest.TestCase):
    """Pruebas unitarias para la sincronización local."""

    def test_upload_download_and_sync(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_dir = os.path.join(tmpdir, "vaults")
            os.makedirs(vault_dir)
            vault_file = os.path.join(vault_dir, "vault.json")
            sync_folder = os.path.join(tmpdir, "cloud")
            # Crear archivo de bóveda
            vault_contents_1 = b"datos1"
            with open(vault_file, "wb") as f:
                f.write(vault_contents_1)
            sync = LocalCloudSync(sync_folder)
            # Subir
            self.assertTrue(sync.upload_vault(vault_file))
            remote_path = os.path.join(sync_folder, "vault.json")
            self.assertTrue(os.path.exists(remote_path))
            # Descargar
            download_file = os.path.join(vault_dir, "vault_copy.json")
            self.assertTrue(sync.download_vault(download_file, "vault.json"))
            self.assertTrue(os.path.exists(download_file))
            with open(download_file, "rb") as f:
                self.assertEqual(f.read(), vault_contents_1)
            # Modificar local y sincronizar (subir)
            time.sleep(1)
            vault_contents_2 = b"datos2"
            with open(vault_file, "wb") as f:
                f.write(vault_contents_2)
            self.assertTrue(sync.sync_vault(vault_file))
            with open(remote_path, "rb") as f:
                self.assertEqual(f.read(), vault_contents_2)
            # Modificar remoto y sincronizar (descargar)
            time.sleep(1)
            remote_contents_3 = b"datos3"
            with open(remote_path, "wb") as f:
                f.write(remote_contents_3)
            self.assertTrue(sync.sync_vault(vault_file))
            with open(vault_file, "rb") as f:
                self.assertEqual(f.read(), remote_contents_3)


if __name__ == '__main__':
    unittest.main()
