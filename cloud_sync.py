"""Compatibilidad con la interfaz original de sincronización en la nube.

Este módulo proporciona la clase :class:`LocalCloudSync` que era
esperada por la interfaz gráfica original.  Internamente utiliza la
implementación de :mod:`password_vault.cloud` para realizar la
sincronización en una carpeta local.
"""

"""Compatibilidad con la interfaz original para sincronización en la nube.

Este módulo define :class:`LocalCloudSync` para mantener la API que la
interfaz gráfica original utilizaba.  La clase hereda de
:class:`password_vault.cloud.LocalCloudSync` y añade los atributos
``cloud_folder`` y ``vault_filename`` esperados por la interfaz para
mostrar el estado de sincronización.

Al llamar a :meth:`sync_vault` se sincroniza la bóveda (como en la
implementación refactorizada) y se actualiza la propiedad
``vault_filename`` con el nombre del archivo de bóveda.  Esto permite
que la interfaz consulte la ruta remota y compare las fechas de
modificación locales y en la nube.
"""

import os
from password_vault.cloud import LocalCloudSync as _BaseLocalCloudSync


class LocalCloudSync(_BaseLocalCloudSync):
    """Sincronizador local con atributos compatibles.

    Hereda del sincronizador refactorizado y expone los atributos
    ``cloud_folder`` y ``vault_filename`` para uso de la interfaz.
    """

    def __init__(self, sync_folder: str) -> None:
        super().__init__(sync_folder)
        # Atributo esperado por la interfaz para mostrar la ruta de nube
        self.cloud_folder: str = sync_folder
        # Nombre de archivo de bóveda sincronizado más recientemente.  Se
        # inicializa como cadena vacía para que os.path.join funcione sin
        # lanzar excepciones (join('dir', '') devuelve 'dir').
        self.vault_filename: str = ""

    def sync_vault(self, vault_file: str) -> bool:
        """Sincroniza la bóveda y actualiza ``vault_filename``.

        Se invoca la lógica de la clase base y luego se registra el
        nombre del archivo de bóveda (sin ruta) en ``vault_filename``.
        """
        # Delegar a la implementación base
        result = super().sync_vault(vault_file)
        # Actualizar el nombre de archivo para que la interfaz pueda
        # construir la ruta completa en la carpeta de sincronización
        self.vault_filename = os.path.basename(vault_file)
        return result


__all__ = ["LocalCloudSync"]