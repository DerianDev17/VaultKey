"""
Utilidades para generación y evaluación de contraseñas.

Este módulo agrupa funciones independientes que pueden utilizarse
tanto en interfaces gráficas como en scripts o servicios de backend.
La generación de contraseñas admite personalización de la longitud y
de los tipos de caracteres incluidos.  La evaluación de fortaleza
calcula un puntaje sencillo basado en la diversidad y longitud de la
contraseña y proporciona recomendaciones de mejora.
"""

from __future__ import annotations

import random
import string
from typing import Dict, List


def generate_password(
    length: int = 16,
    include_lower: bool = True,
    include_upper: bool = True,
    include_digits: bool = True,
    include_symbols: bool = True,
) -> str:
    """
    Genera una contraseña aleatoria según los parámetros indicados.

    :param length: Longitud total de la contraseña. Debe ser mayor a cero.
    :param include_lower: Incluir letras minúsculas.
    :param include_upper: Incluir letras mayúsculas.
    :param include_digits: Incluir dígitos numéricos.
    :param include_symbols: Incluir caracteres de símbolos.
    :return: Contraseña generada al azar.
    :raises ValueError: Si la longitud es menor o igual a cero o no se
        selecciona ningún grupo de caracteres.
    """
    if length <= 0:
        raise ValueError("La longitud de la contraseña debe ser mayor que 0")
    # Construir el conjunto de caracteres permitidos
    pools: List[str] = []
    character_pool = ""
    if include_lower:
        pools.append(string.ascii_lowercase)
        character_pool += string.ascii_lowercase
    if include_upper:
        pools.append(string.ascii_uppercase)
        character_pool += string.ascii_uppercase
    if include_digits:
        pools.append(string.digits)
        character_pool += string.digits
    if include_symbols:
        symbols = "!@#$%^&*()-_=+[]{};:,.<>?/"
        pools.append(symbols)
        character_pool += symbols
    if not character_pool:
        raise ValueError(
            "Debe seleccionar al menos un tipo de caracteres para generar la contraseña"
        )
    # Asegurar que se incluye al menos un carácter de cada grupo seleccionado
    password_chars: List[str] = []
    for pool in pools:
        password_chars.append(random.choice(pool))
    # Completar el resto de la contraseña
    while len(password_chars) < length:
        password_chars.append(random.choice(character_pool))
    # Mezclar para evitar patrones predecibles
    random.shuffle(password_chars)
    return "".join(password_chars)


def check_password_strength(password: str) -> Dict[str, object]:
    """
    Evalúa la fortaleza de una contraseña y devuelve un reporte.

    El puntaje se calcula sumando puntos por cada tipo de carácter
    presente (minúscula, mayúscula, dígito y símbolo) y por la
    longitud. Además, se generan recomendaciones básicas para mejorar
    contraseñas débiles.

    :param password: Contraseña a evaluar.
    :return: Diccionario con las claves ``strength`` (cadena), ``score`` (int) y
        ``feedback`` (lista de sugerencias).
    """
    length = len(password)
    score = 0
    feedback: List[str] = []

    # Comprobar presencia de cada tipo de carácter
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    symbols_set = set("!@#$%^&*()-_=+[]{};:,.<>?/")
    has_symbol = any(c in symbols_set for c in password)

    if has_lower:
        score += 1
    else:
        feedback.append("Añade letras minúsculas")
    if has_upper:
        score += 1
    else:
        feedback.append("Añade letras mayúsculas")
    if has_digit:
        score += 1
    else:
        feedback.append("Añade dígitos")
    if has_symbol:
        score += 1
    else:
        feedback.append("Añade símbolos (p. ej. !@#$)")

    # Puntos por longitud: 1 punto si >= 12, 2 si >= 16
    if length >= 16:
        score += 2
    elif length >= 12:
        score += 1
    else:
        feedback.append("Usa al menos 12 caracteres")

    # Determinar categoría
    if score <= 2:
        strength = "Débil"
    elif score <= 4:
        strength = "Mediana"
    else:
        strength = "Fuerte"

    return {"strength": strength, "score": score, "feedback": feedback}
