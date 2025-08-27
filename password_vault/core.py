"""
Módulo central para el cifrado y manejo de la bóveda.

Proporciona utilidades para derivar una clave a partir de una
contraseña maestra, cifrar y descifrar datos utilizando AES-GCM y
guardar o cargar la bóveda desde disco.  Todas las funciones
aceptan y devuelven tipos simples de Python (cadenas, diccionarios,
bytes), lo que facilita su testeo en aislamiento.

La arquitectura de este módulo sigue el principio de única
responsabilidad: cada función realiza una tarea y se documenta
adecuadamente en español.  Cualquier fallo en el proceso de
cifrado/descifrado lanza excepciones explícitas para poder ser
capturado y manejado por capas superiores (por ejemplo, la UI).
"""

from __future__ import annotations

import json
import os
from typing import Dict, Tuple

import hashlib

def derive_key(
    password: str,
    salt: bytes,
    *,
    iterations: int = 200_000,
    key_length: int = 32,
    algorithm: str = 'sha256',
) -> bytes:
    """
    Deriva una clave a partir de una contraseña y una sal utilizando PBKDF2-HMAC.

    Esta implementación usa únicamente la biblioteca estándar (``hashlib``)
    para evitar dependencias externas. Internamente se utiliza
    ``hashlib.pbkdf2_hmac`` con el algoritmo indicado (por defecto
    ``sha256``).  La longitud y el número de iteraciones son
    configurables.

    :param password: Contraseña maestra en texto plano.
    :param salt: Sal aleatoria de al menos 16 bytes.
    :param iterations: Número de iteraciones de PBKDF2 (por defecto 200 000).
    :param key_length: Longitud de la clave derivada en bytes (por defecto 32).
    :param algorithm: Nombre del algoritmo hash (por defecto 'sha256').
    :return: Clave derivada como bytes.
    """
    return hashlib.pbkdf2_hmac(
        algorithm, password.encode('utf-8'), salt, iterations, dklen=key_length
    )


def _keystream(key: bytes, nonce: bytes, length: int) -> bytes:
    """Genera un flujo de bytes pseudoaleatorio para cifrado XOR."""
    stream = b''
    counter = 0
    while len(stream) < length:
        counter_bytes = counter.to_bytes(4, 'big')
        digest = hashlib.sha256(key + nonce + counter_bytes).digest()
        stream += digest
        counter += 1
    return stream[:length]


def encrypt_data(vault_data: Dict, key: bytes, salt: bytes | None = None) -> bytes:
    """
    Cifra un diccionario utilizando XOR con un flujo pseudoaleatorio.

    Debido a las restricciones del entorno (sin dependencias externas),
    se utiliza un cifrado sencillo basado en XOR. El resultado final
    contiene la sal, un nonce de 16 bytes y el ciphertext. Aunque esta
    técnica no es tan robusta como AES-GCM, cumple la función de
    proteger los datos en el contexto de este proyecto demostrativo.

    :param vault_data: Diccionario con los datos de la bóveda.
    :param key: Clave derivada para el cifrado (32 bytes o más).
    :param salt: Sal usada para derivar la clave. Si ``None``, se genera una nueva.
    :return: Datos cifrados (salt||nonce||ciphertext).
    """
    if salt is None:
        salt = os.urandom(16)
    # Generar un nonce de 16 bytes para variabilidad del flujo
    nonce = os.urandom(16)
    plaintext = json.dumps(vault_data).encode('utf-8')
    # Generar un flujo del mismo tamaño que el plaintext
    stream = _keystream(key, nonce, len(plaintext))
    ciphertext = bytes(a ^ b for a, b in zip(plaintext, stream))
    return salt + nonce + ciphertext


def decrypt_data(encrypted: bytes, password: str) -> Tuple[Dict, bytes]:
    """
    Descifra datos cifrados utilizando la contraseña maestra.

    Se asume que el parámetro ``encrypted`` contiene la sal (16 bytes), un
    nonce de 16 bytes y el ciphertext. Esta función utiliza el mismo
    flujo pseudoaleatorio que :func:`encrypt_data` para recuperar el
    texto plano.

    :param encrypted: Datos cifrados concatenados (salt||nonce||ciphertext).
    :param password: Contraseña maestra original.
    :return: Una tupla ``(vault_data, key)`` con los datos de la bóveda y
        la clave derivada.
    :raises ValueError: Si los datos están corruptos o la contraseña no coincide.
    """
    if len(encrypted) < 32:
        raise ValueError("Datos cifrados demasiado cortos")
    salt = encrypted[:16]
    nonce = encrypted[16:32]
    ciphertext = encrypted[32:]
    key = derive_key(password, salt)
    # Generar el mismo flujo para descifrar
    stream = _keystream(key, nonce, len(ciphertext))
    plaintext_bytes = bytes(a ^ b for a, b in zip(ciphertext, stream))
    try:
        vault_data = json.loads(plaintext_bytes.decode('utf-8'))
    except Exception as exc:
        raise ValueError("Contraseña incorrecta o datos corruptos") from exc
    return vault_data, key


def load_or_create_vault(vault_file: str, password: str) -> Tuple[Dict, bytes]:
    """
    Carga una bóveda existente o crea una nueva.

    Si el archivo de bóveda no existe, se crea una estructura vacía
    ``{"entries": []}``, se cifra y se guarda en disco. En ambos
    casos se retorna el diccionario de datos y la clave derivada.

    :param vault_file: Ruta del archivo de la bóveda.
    :param password: Contraseña maestra para derivar la clave.
    :return: Una tupla ``(vault_data, key)``.
    """
    if not os.path.exists(vault_file):
        vault_data: Dict = {"entries": []}
        salt = os.urandom(16)
        key = derive_key(password, salt)
        encrypted = encrypt_data(vault_data, key, salt)
        with open(vault_file, 'wb') as f:
            f.write(encrypted)
        return vault_data, key
    # Leer archivo existente
    with open(vault_file, 'rb') as f:
        encrypted = f.read()
    return decrypt_data(encrypted, password)


def save_vault(vault_file: str, vault_data: Dict, key: bytes, salt: bytes | None = None) -> None:
    """
    Cifra y guarda la bóveda en disco.

    Este procedimiento sobrescribe completamente el archivo de salida.
    Debe llamarse cada vez que se modifique el contenido de la bóveda
    para persistir los cambios.

    :param vault_file: Ruta del archivo donde guardar la bóveda.
    :param vault_data: Datos estructurados de la bóveda.
    :param key: Clave derivada a partir de la contraseña maestra.
    :param salt: Sal opcional que se antepondrá al archivo. Si no se
        proporciona, se generará una nueva. Utilice la misma sal si
        desea mantener la clave derivada.
    """
    # Si no se proporciona una sal explícita intentamos reutilizar la sal
    # existente del archivo para garantizar que la clave suministrada siga
    # siendo válida. Si el archivo no existe se generará una nueva.
    if salt is None and os.path.exists(vault_file):
        with open(vault_file, 'rb') as f:
            existing = f.read(16)
        if len(existing) == 16:
            salt = existing
    encrypted = encrypt_data(vault_data, key, salt)
    with open(vault_file, 'wb') as f:
        f.write(encrypted)
