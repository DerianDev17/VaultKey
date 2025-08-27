"""Compatibilidad con la interfaz original para generación de contraseñas.

Las interfaces de usuario originales importaban funciones desde
``password_generator``.  Este archivo reexporta las funciones
equivalentes de :mod:`password_vault.password_utils`.
"""

from password_vault.password_utils import generate_password, check_password_strength  # noqa: F401

__all__ = [
    "generate_password",
    "check_password_strength",
]