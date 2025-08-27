"""
Herramientas de auditoría de seguridad para la bóveda.

Incluye la clase :class:`SecurityAudit` que analiza el contenido de la
bóveda para detectar contraseñas débiles, duplicadas o faltantes y
genera un informe estructurado.  Además, se define :class:`SecureClipboard`
para gestionar el portapapeles de forma segura, borrando su contenido
después de un intervalo configurable.

Estas clases son independientes de la interfaz y pueden emplearse
tanto en aplicaciones gráficas como en scripts de línea de comandos.
"""

from __future__ import annotations

import threading
import time
try:
    # Tkinter puede no estar disponible en algunos entornos (por ejemplo, servidores).
    import tkinter as tk  # type: ignore
except ImportError:
    tk = None  # type: ignore

from typing import Dict, List, Any

from .password_utils import check_password_strength


class SecurityAudit:
    """Auditoría de seguridad para la bóveda de contraseñas."""

    def __init__(self) -> None:
        self.audit_results: Dict[str, Any] = {}

    def audit_vault(self, vault_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza las entradas de la bóveda y devuelve un informe.

        El informe contiene el número total de entradas, listas de
        contraseñas débiles, duplicadas y una lista de recomendaciones.
        La detección de contraseñas comprometidas podría integrarse
        utilizando servicios externos, pero no se implementa aquí para
        mantener la simplicidad y evitar dependencias de red.

        :param vault_data: Estructura de la bóveda cargada desde disco.
        :return: Informe con estadísticas y recomendaciones.
        """
        entries = vault_data.get("entries", [])
        total = len(entries)
        weak_passwords: List[Dict[str, Any]] = []
        duplicates: List[Dict[str, Any]] = []
        breached: List[Dict[str, Any]] = []  # no implementado

        # Detectar contraseñas duplicadas usando un diccionario inverso
        seen_passwords: Dict[str, Dict[str, Any]] = {}
        for entry in entries:
            pwd = entry.get("password", "")
            # Evaluar fortaleza
            strength = check_password_strength(pwd)
            if strength["strength"] == "Débil":
                weak_passwords.append({"title": entry.get("title", "Sin título"), **strength})
            # Revisar duplicados
            if pwd in seen_passwords:
                duplicates.append(entry)
            else:
                seen_passwords[pwd] = entry

        recommendations: List[str] = []
        if weak_passwords:
            recommendations.append(
                "Reemplaza las contraseñas débiles por contraseñas más largas y variadas"
            )
        if duplicates:
            recommendations.append(
                "Evita reutilizar la misma contraseña en varias entradas"
            )

        self.audit_results = {
            "total_entries": total,
            "weak_passwords": weak_passwords,
            "duplicate_passwords": duplicates,
            "breached_passwords": breached,
            "recommendations": recommendations,
        }
        return self.audit_results

    def run_audit(self, vault_data: Dict[str, Any]) -> List[str]:
        """
        Ejecuta la auditoría y devuelve una lista de mensajes legibles.

        :param vault_data: Datos de la bóveda.
        :return: Lista de resultados en forma de cadenas descriptivas.
        """
        report = self.audit_vault(vault_data)
        messages: List[str] = []
        messages.append(f"Entradas totales: {report['total_entries']}")
        if report["weak_passwords"]:
            messages.append(
                f"Contraseñas débiles: {len(report['weak_passwords'])}"
            )
        if report["duplicate_passwords"]:
            messages.append(
                f"Contraseñas duplicadas: {len(report['duplicate_passwords'])}"
            )
        if report["breached_passwords"]:
            messages.append(
                f"Contraseñas comprometidas: {len(report['breached_passwords'])}"
            )
        if report["recommendations"]:
            messages.extend(report["recommendations"])
        return messages


class SecureClipboard:
    """
    Portapapeles seguro que borra automáticamente su contenido.

    Esta implementación usa :mod:`tkinter` para acceder al portapapeles.
    Cuando se copia un texto se programa un temporizador que lo
    eliminará pasados ``clear_time`` segundos.  Esta clase es útil
    para minimizar la exposición de datos sensibles en el portapapeles.
    """

    def __init__(self, clear_time: int = 30) -> None:
        """
        Inicializa el portapapeles seguro.

        :param clear_time: Tiempo en segundos tras el cual se borra el
            portapapeles. Por defecto 30 segundos.
        """
        self.clear_time = clear_time
        self._root = None  # type: ignore

    def copy(self, text: str) -> None:
        """
        Copia un texto al portapapeles y programa su borrado.

        Si ``tkinter`` no está disponible, la operación no tendrá efecto
        pero tampoco lanzará una excepción. Esto permite usar el
        auditor sin interfaz gráfica en entornos donde no se disponga
        de un portapapeles (por ejemplo, servidores headless).

        :param text: Texto a copiar en el portapapeles.
        """
        if tk is None:
            # Tkinter no está disponible; omitir operación silenciosamente
            return
        if self._root is None:
            self._root = tk.Tk()
            self._root.withdraw()
        self._root.clipboard_clear()
        self._root.clipboard_append(text)
        timer = threading.Timer(self.clear_time, self.clear_clipboard)
        timer.start()

    def clear_clipboard(self) -> None:
        """Elimina el contenido del portapapeles si existe."""
        if tk is None or self._root is None:
            return
        try:
            self._root.clipboard_clear()
        except Exception:
            pass
