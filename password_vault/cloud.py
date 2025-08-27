"""
Sincronización local simulada para la bóveda de contraseñas.

Este módulo implementa una sincronización básica entre un archivo
local de la bóveda y una carpeta que actúa como "nube".  No utiliza
conexiones de red reales, pero su interfaz está pensada para poder
ser sustituida por una implementación real en un futuro.

Las operaciones incluidas son:

- Subir (upload) una bóveda a la carpeta de sincronización.
- Descargar (download) una bóveda desde la carpeta de sincronización a
  una ruta específica.
- Sincronizar (sync) comparando marcas de tiempo para determinar qué
  versión está más actualizada y copiarla en consecuencia.

Todas las operaciones retornan un booleano indicando el éxito y
lanzan excepciones cuando ocurre un error inesperado.
"""

from __future__ import annotations

import os
import shutil
from typing import Optional


class LocalCloudSync:
    """Sincronizador local que emula una nube usando el sistema de archivos."""

    def __init__(self, sync_folder: str) -> None:
        """
        Inicializa el sincronizador y crea la carpeta de sincronización si no existe.

        :param sync_folder: Carpeta en la que se almacenarán las copias de la bóveda.
        """
        self.sync_folder = sync_folder
        if not os.path.exists(self.sync_folder):
            os.makedirs(self.sync_folder)

    def upload_vault(self, vault_file: str) -> bool:
        """
        Copia el archivo de la bóveda a la carpeta de sincronización.

        :param vault_file: Ruta del archivo de la bóveda a subir.
        :return: ``True`` si la operación se completó correctamente.
        :raises FileNotFoundError: Si el archivo de bóveda no existe.
        """
        if not os.path.isfile(vault_file):
            raise FileNotFoundError(f"Archivo de bóveda no encontrado: {vault_file}")
        destination = os.path.join(self.sync_folder, os.path.basename(vault_file))
        shutil.copy2(vault_file, destination)
        return True

    def download_vault(self, destination: str, vault_name: Optional[str] = None) -> bool:
        """
        Descarga la bóveda desde la carpeta de sincronización a una ruta.

        Si ``vault_name`` no se especifica, se utiliza el nombre de archivo
        presente en la carpeta de sincronización. Esta función sobrescribe
        cualquier archivo existente en ``destination``.

        :param destination: Ruta de destino para el archivo descargado.
        :param vault_name: Nombre de archivo en la carpeta de sincronización.
        :return: ``True`` si se descargó correctamente, ``False`` si no existe en la nube.
        """
        if vault_name is None:
            # Tomar cualquier archivo con extensión .json en la carpeta de sincronización
            candidates = [f for f in os.listdir(self.sync_folder) if f.endswith('.json')]
            if not candidates:
                return False
            vault_name = candidates[0]
        source = os.path.join(self.sync_folder, vault_name)
        if not os.path.exists(source):
            return False
        shutil.copy2(source, destination)
        return True

    def sync_vault(self, vault_file: str) -> bool:
        """
        Sincroniza la bóveda local con la copia en la carpeta de sincronización.

        Si la copia en la nube es más reciente que la local, se descarga.
        Si la copia local es más reciente, se sube. Si no existe ninguna
        copia en la nube, se crea subiendo la local.

        :param vault_file: Ruta de la bóveda local.
        :return: ``True`` si se realizó alguna acción de sincronización, ``False`` si no fue necesaria.
        """
        local_exists = os.path.exists(vault_file)
        remote_path = os.path.join(self.sync_folder, os.path.basename(vault_file))
        remote_exists = os.path.exists(remote_path)

        if not local_exists and not remote_exists:
            # Nada que sincronizar
            return False
        if local_exists and not remote_exists:
            # Subir primera copia
            self.upload_vault(vault_file)
            return True
        if not local_exists and remote_exists:
            # Descargar si no existe localmente
            shutil.copy2(remote_path, vault_file)
            return True

        # Ambos existen, comparar fechas de modificación
        local_mtime = os.path.getmtime(vault_file)
        remote_mtime = os.path.getmtime(remote_path)
        if local_mtime > remote_mtime:
            # Local más reciente, subir
            self.upload_vault(vault_file)
            return True
        elif remote_mtime > local_mtime:
            # Remoto más reciente, descargar
            shutil.copy2(remote_path, vault_file)
            return True
        return False
