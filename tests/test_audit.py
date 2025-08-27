import unittest

from password_vault.audit import SecurityAudit


class TestAudit(unittest.TestCase):
    """Pruebas para la auditoría de seguridad."""

    def test_audit_detects_weak_and_duplicate_passwords(self):
        vault_data = {
            "entries": [
                {"title": "Sitio A", "password": "123456"},
                {"title": "Sitio B", "password": "123456"},
                {"title": "Sitio C", "password": "Abcdef1!"},
            ]
        }
        auditor = SecurityAudit()
        report = auditor.audit_vault(vault_data)
        self.assertEqual(len(report["weak_passwords"]), 2)
        self.assertEqual(len(report["duplicate_passwords"]), 1)
        self.assertTrue(report["recommendations"])


if __name__ == '__main__':
    unittest.main()
