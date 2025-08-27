import unittest

from password_vault.password_utils import generate_password, check_password_strength


class TestPasswordUtils(unittest.TestCase):
    """Pruebas unitarias para las utilidades de contraseñas."""

    def test_generate_password_character_types(self):
        pwd = generate_password(length=10, include_lower=True, include_upper=False, include_digits=True, include_symbols=False)
        self.assertEqual(len(pwd), 10)
        self.assertTrue(any(c.islower() for c in pwd))
        self.assertTrue(any(c.isdigit() for c in pwd))
        self.assertFalse(any(c.isupper() for c in pwd))
        self.assertFalse(any(c in "!@#$%^&*()-_=+[]{};:,.<>?/" for c in pwd))

    def test_generate_password_invalid_parameters(self):
        with self.assertRaises(ValueError):
            generate_password(0)
        with self.assertRaises(ValueError):
            generate_password(8, False, False, False, False)

    def test_check_password_strength_scores(self):
        weak = check_password_strength("abcd123")
        self.assertEqual(weak["strength"], "Débil")
        med = check_password_strength("Abcd1234")
        self.assertIn(med["strength"], {"Mediana", "Fuerte"})
        strong = check_password_strength("Abcd1234!@#XYZ")
        self.assertEqual(strong["strength"], "Fuerte")
        self.assertGreaterEqual(len(weak["feedback"]), 1)


if __name__ == '__main__':
    unittest.main()
