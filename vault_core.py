"""Compatibilidad con la interfaz original del gestor.

Este módulo actúa como un puente entre el código de la interfaz de
usuario original (que esperaba un módulo llamado ``vault_core``) y la
implementación refactorizada en :mod:`password_vault.core`.  Se
reexportan las funciones necesarias para cargar/guardar la bóveda y
derivar claves de cifrado.  De este modo, la interfaz de escritorio
o móvil existente puede seguir importando ``vault_core`` sin cambios.
"""

from password_vault.core import derive_key, load_or_create_vault, save_vault  # noqa: F401

__all__ = [
    "derive_key",
    "load_or_create_vault",
    "save_vault",
]