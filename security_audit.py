"""Compatibilidad con la interfaz original para auditoría y portapapeles.

Este módulo reexporta las clases :class:`SecurityAudit` y
:class:`SecureClipboard` de :mod:`password_vault.audit` para que la
interfaz gráfica original pueda importarlas sin cambios.  La clase
``SecurityAudit`` de la refactorización proporciona los métodos
``audit_vault`` y ``run_audit`` que la interfaz espera, y
``SecureClipboard`` mantiene el comportamiento de borrado automático
del portapapeles.
"""

# Reexportar directamente las implementaciones completas de la
# refactorización.  De este modo se mantienen todas las
# funcionalidades de auditoría (contraseñas débiles, duplicadas, etc.)
from password_vault.audit import SecurityAudit, SecureClipboard

__all__ = ["SecurityAudit", "SecureClipboard"]