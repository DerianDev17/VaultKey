"""
Interfaz de línea de comandos para la bóveda de contraseñas.

Esta CLI proporciona una manera sencilla de crear o abrir una bóveda,
agregar entradas, listar las entradas existentes, eliminar entradas y
realizar una auditoría. Está pensada como ejemplo didáctico y no
incluye todas las características avanzadas de la interfaz gráfica.

El flujo básico es el siguiente:

1. El usuario ingresa una contraseña maestra. Si la bóveda aún no
   existe se crea automáticamente.
2. Se presenta un menú con opciones para listar, agregar, eliminar,
   auditar o salir.
3. Cada acción invoca funciones del módulo :mod:`core` y :mod:`audit`.
"""

from __future__ import annotations

import getpass
import os
from typing import Dict, Any

from .core import load_or_create_vault, save_vault
from .audit import SecurityAudit
from .auth import authenticate, create_user, load_user_db


def prompt_entry() -> Dict[str, str]:
    """Solicita al usuario los campos de una entrada de bóveda."""
    title = input("Título de la entrada: ").strip()
    username = input("Nombre de usuario (opcional): ").strip()
    password = getpass.getpass("Contraseña: ")
    return {"title": title, "username": username, "password": password}


def main() -> None:
    """Función principal de la CLI con inicio de sesión de usuarios.

    Este flujo solicita primero las credenciales del usuario y almacena
    las cuentas en un archivo JSON (por defecto ``users.json``).  Si
    el usuario no existe, se ofrece registrarlo.  Una vez autenticado
    con éxito, se utiliza una contraseña maestra para cifrar la bóveda
    del usuario.  Cada usuario tiene su propia bóveda, cuyo nombre por
    defecto es ``<usuario>_vault.json``.
    """
    print("\nGestor de Contraseñas CLI")
    print("=" * 30)

    # Base de datos de usuarios
    user_db_file = input("Ruta del archivo de usuarios [users.json]: ").strip() or "users.json"
    username = input("Nombre de usuario: ").strip()
    if not username:
        print("Debe especificar un nombre de usuario. Saliendo...")
        return
    password = getpass.getpass("Contraseña: ")

    # Intentar autenticar; si el usuario no existe, ofrecer registrarlo
    if not authenticate(username, password, user_db_file):
        db = load_user_db(user_db_file)
        if username not in db:
            resp = input("Usuario no encontrado. ¿Desea registrarse? [s/N]: ").strip().lower()
            if resp == 's':
                try:
                    create_user(username, password, user_db_file)
                    print("Usuario registrado correctamente.")
                except ValueError as exc:
                    print(f"Error al crear el usuario: {exc}")
                    return
            else:
                print("No se pudo iniciar sesión. Saliendo...")
                return
        else:
            print("Contraseña incorrecta. Saliendo...")
            return
    else:
        print("Inicio de sesión exitoso.")

    # Solicitar contraseña maestra para cifrar la bóveda.  Puede ser
    # diferente de la contraseña de inicio de sesión, aunque en muchos
    # casos se usa la misma.
    master_password = getpass.getpass("Contraseña maestra de la bóveda: ")

    # Seleccionar archivo de bóveda; por defecto se usa un nombre
    # asociado al usuario pero se permite sobreescribirlo.
    default_vault = f"{username}_vault.json"
    vault_file_input = input(f"Ruta del archivo de la bóveda [{default_vault}]: ").strip()
    vault_file = vault_file_input or default_vault

    # Cargar o crear la bóveda usando la contraseña maestra
    try:
        vault_data, key = load_or_create_vault(vault_file, master_password)
    except ValueError as exc:
        print(f"Error al abrir la bóveda: {exc}")
        return

    # Menú interactivo
    while True:
        print("\nOpciones:")
        print("1) Listar entradas")
        print("2) Agregar entrada")
        print("3) Eliminar entrada")
        print("4) Auditoría de seguridad")
        print("5) Guardar y salir")
        choice = input("Selecciona una opción [1-5]: ").strip()
        if choice == "1":
            if not vault_data["entries"]:
                print("No hay entradas guardadas.")
            else:
                for idx, entry in enumerate(vault_data["entries"], start=1):
                    print(f"{idx}. {entry.get('title', 'Sin título')} (usuario: {entry.get('username', '')})")
        elif choice == "2":
            entry = prompt_entry()
            vault_data["entries"].append(entry)
            print("Entrada agregada.")
        elif choice == "3":
            idx_str = input("Número de entrada a eliminar: ").strip()
            if not idx_str.isdigit():
                print("Índice no válido.")
                continue
            idx = int(idx_str) - 1
            if 0 <= idx < len(vault_data["entries"]):
                removed = vault_data["entries"].pop(idx)
                print(f"Entrada '{removed.get('title', '')}' eliminada.")
            else:
                print("Índice fuera de rango.")
        elif choice == "4":
            audit = SecurityAudit()
            report = audit.audit_vault(vault_data)
            print(f"Entradas totales: {report['total_entries']}")
            print(f"Contraseñas débiles: {len(report['weak_passwords'])}")
            print(f"Contraseñas duplicadas: {len(report['duplicate_passwords'])}")
            if report['recommendations']:
                print("Recomendaciones:")
                for rec in report['recommendations']:
                    print(f" • {rec}")
        elif choice == "5":
            save_vault(vault_file, vault_data, key)
            print("Cambios guardados. Saliendo...")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
