"""
Paquete de la aplicación de gestor de contraseñas.

Este paquete contiene todos los módulos necesarios para
proporcionar un gestor de contraseñas modular y probado en Python.

Estructura de módulos:

- :mod:`core`: Funciones para cifrar, descifrar y gestionar el
  archivo de la bóveda. Separa la lógica criptográfica y de
  persistencia en unidades pequeñas para facilitar el testeo.
- :mod:`password_utils`: Utilidades para generar contraseñas seguras y
  evaluar su fortaleza. Estas funciones no dependen de la interfaz
  gráfica y pueden reutilizarse en otros contextos.
- :mod:`cloud`: Implementación de un sincronizador local que actúa como
  "nube" simulada. Permite subir, descargar y sincronizar el
  archivo de la bóveda entre dispositivos o directorios.
- :mod:`audit`: Herramientas de auditoría de seguridad y un portapapeles
  seguro que borra automáticamente su contenido tras un tiempo.
- :mod:`cli`: Interfaz de línea de comandos simple para interactuar
  con la bóveda. Esta interfaz es opcional y sirve como ejemplo de
  uso de los módulos anteriores.

Cada módulo está diseñado para ser autocontenido y con
documentación en español para facilitar su comprensión.
"""

from .core import derive_key, encrypt_data, decrypt_data, load_or_create_vault, save_vault  # noqa: F401
from .password_utils import generate_password, check_password_strength  # noqa: F401
from .cloud import LocalCloudSync  # noqa: F401
from .audit import SecurityAudit, SecureClipboard  # noqa: F401
from .auth import create_user, authenticate, load_user_db, save_user_db  # noqa: F401
