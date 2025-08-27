"""
Gestión de usuarios y autenticación.

Este módulo permite registrar usuarios y validar sus credenciales. Las
contraseñas se almacenan utilizando PBKDF2-HMAC con una sal
individual por usuario y un número elevado de iteraciones para
dificultar ataques de fuerza bruta. Los datos de los usuarios se
persisten en un archivo JSON cuyo nombre se pasa como parámetro.
"""

from __future__ import annotations

import json
import os
import hashlib
from typing import Dict, Any, Tuple


def _derive_password_hash(password: str, salt: bytes, iterations: int = 200_000, key_length: int = 32) -> bytes:
    """
    Deriva un hash de contraseña usando PBKDF2-HMAC-SHA256.

    :param password: Contraseña en texto plano.
    :param salt: Sal aleatoria asociada al usuario.
    :param iterations: Número de iteraciones PBKDF2.
    :param key_length: Longitud del hash derivado.
    :return: Hash de la contraseña.
    """
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations, dklen=key_length)


def load_user_db(db_file: str) -> Dict[str, Any]:
    """Carga la base de datos de usuarios desde un archivo JSON.

    Si el archivo no existe o está vacío/corrupto, se devuelve
    un diccionario vacío.  Esto evita errores al inicializar una nueva
    base de datos de usuarios.
    """
    if not os.path.exists(db_file):
        return {}
    try:
        with open(db_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        # El archivo existe pero no contiene JSON válido; se retorna una
        # base vacía para permitir la inicialización
        return {}


def save_user_db(db_file: str, db: Dict[str, Any]) -> None:
    """Guarda la base de datos de usuarios en un archivo JSON."""
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2)


def create_user(username: str, password: str, db_file: str) -> None:
    """
    Registra un nuevo usuario con contraseña.

    :param username: Nombre de usuario único.
    :param password: Contraseña en texto plano.
    :param db_file: Ruta del archivo de base de datos de usuarios.
    :raises ValueError: Si el usuario ya existe.
    """
    db = load_user_db(db_file)
    if username in db:
        raise ValueError("El usuario ya existe")
    salt = os.urandom(16)
    pwd_hash = _derive_password_hash(password, salt)
    db[username] = {
        'salt': salt.hex(),
        'pwd_hash': pwd_hash.hex(),
        'iterations': 200_000,
        'key_length': 32,
    }
    save_user_db(db_file, db)


def authenticate(username: str, password: str, db_file: str) -> bool:
    """
    Verifica si las credenciales del usuario son correctas.

    :param username: Nombre de usuario.
    :param password: Contraseña en texto plano proporcionada por el usuario.
    :param db_file: Ruta del archivo de base de datos de usuarios.
    :return: ``True`` si las credenciales son válidas, ``False`` en caso contrario.
    """
    db = load_user_db(db_file)
    user = db.get(username)
    if not user:
        return False
    salt = bytes.fromhex(user['salt'])
    iterations = user.get('iterations', 200_000)
    key_length = user.get('key_length', 32)
    pwd_hash = _derive_password_hash(password, salt, iterations=iterations, key_length=key_length)
    return pwd_hash.hex() == user['pwd_hash']
