"""CLI simple para gestión de usuarios.

Esta interfaz permite crear nuevos usuarios y autenticar usuarios
existentes desde la línea de comandos.  Los datos se almacenan en un
archivo JSON gestionado por :mod:`password_vault.auth`.

Ejemplo de uso::

    python -m password_vault.user_cli

El script solicitará el nombre de usuario y la contraseña.  Si el
usuario no existe, ofrecerá registrarlo automáticamente.
"""
from __future__ import annotations

import getpass

from .auth import authenticate, create_user, load_user_db


def main() -> None:
    """Punto de entrada de la interfaz de usuarios.

    Primero se solicita la ruta del archivo de base de datos.  Luego se
    pide un nombre de usuario y la contraseña.  Si las credenciales son
    válidas se muestra un mensaje de éxito.  En caso contrario, si el
    usuario no existe, se ofrece registrarlo.
    """
    print("\nGestión de usuarios")
    print("=" * 20)

    db_file = input("Archivo de usuarios [users.json]: ").strip() or "users.json"
    username = input("Nombre de usuario: ").strip()
    if not username:
        print("Debe proporcionar un nombre de usuario. Saliendo...")
        return
    password = getpass.getpass("Contraseña: ")

    # Intentar autenticación
    if authenticate(username, password, db_file):
        print("Inicio de sesión exitoso.")
        return

    # En este punto o el usuario no existe o la contraseña es incorrecta
    db = load_user_db(db_file)
    if username in db:
        print("Contraseña incorrecta. Saliendo...")
        return

    # Ofrecer registrar nuevo usuario
    resp = input("Usuario no encontrado. ¿Desea registrarse? [s/N]: ").strip().lower()
    if resp == "s":
        try:
            create_user(username, password, db_file)
            print("Usuario registrado correctamente.")
        except ValueError as exc:
            # Podría ocurrir si otro proceso creó el usuario antes
            print(f"Error al crear el usuario: {exc}")
    else:
        print("Registro cancelado.")


if __name__ == "__main__":  # pragma: no cover - ejecución directa
    main()
