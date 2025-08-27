# VaultKey – Gestor de Contraseñas Profesional

VaultKey es un gestor de contraseñas modular escrito en **Python** que
permite almacenar, generar y auditar contraseñas de forma segura.  El
proyecto está completamente documentado en español y está pensado como una
solución lista para usar desde la línea de comandos, con interfaces
gráficas opcionales para escritorio y móvil.

## Tabla de contenido

1. [Características](#características)
2. [Requisitos](#requisitos)
3. [Instalación](#instalación)
4. [Uso rápido](#uso-rápido)
5. [Estructura del proyecto](#estructura-del-proyecto)
6. [Pruebas](#pruebas)
7. [Interfaces gráficas](#interfaces-gráficas)
8. [Notas de diseño](#notas-de-diseño)
9. [Contribuir](#contribuir)

## Características

- **Cifrado de datos** mediante una clave derivada de una contraseña
  maestra. La información de la bóveda se almacena siempre cifrada en
  disco.
- **Generación de contraseñas seguras** con longitud y tipos de
  caracteres configurables.
- **Evaluación de fortaleza** que asigna un puntaje y ofrece
  recomendaciones para mejorar.
- **Sincronización local** (sin necesidad de Internet) que simula una
  carpeta en la nube para subir y descargar la bóveda.
- **Auditoría de seguridad** para detectar contraseñas débiles o
  duplicadas.
- **CLI interactiva** para crear, abrir y gestionar la bóveda desde la
  terminal.
- **Soporte multiusuario**: cada usuario cuenta con su propia bóveda
  protegida por una contraseña maestra.

## Requisitos

- Python **3.10** o superior.
- La línea de comandos no requiere dependencias externas.
- Para las interfaces gráficas se deben instalar manualmente
  `customtkinter` (escritorio) y `kivy` (móvil).

## Instalación

```bash
git clone <url_del_repositorio>
cd VaultKey
# Opcional: crear entorno virtual
python -m venv venv && source venv/bin/activate
```

No es necesario instalar paquetes adicionales para la versión de CLI.

## Uso rápido

Ejecuta la interfaz de línea de comandos con gestión de usuarios:

```bash
python -m password_vault.cli
```

El programa solicitará el nombre de usuario y la contraseña de acceso.
Si el usuario no existe, se ofrecerá registrarlo. Tras la autenticación
se pedirá una contraseña maestra para cifrar la bóveda. El archivo se
almacenará por defecto como `<usuario>_vault.json`.

## Estructura del proyecto

```text
VaultKey/
├── password_vault/        # Paquete principal
│   ├── __init__.py
│   ├── core.py            # Cifrado y gestión de archivos
│   ├── password_utils.py  # Generación y evaluación de contraseñas
│   ├── cloud.py           # Sincronización local de la bóveda
│   ├── audit.py           # Auditoría de seguridad y portapapeles
│   ├── auth.py            # Gestión de usuarios e inicio de sesión
│   └─ cli.py           # Interfaz de línea de comandos
├── tests/                 # Pruebas unitarias
└─ README.md
```

Cada módulo está diseñado con una sola responsabilidad y cuenta con
documentación clara.

## Pruebas

Las pruebas unitarias se encuentran en `tests`. Puedes ejecutarlas con
`pytest` (o `unittest` si lo prefieres):

```bash
python -m pytest
```

## Interfaces gráficas

El proyecto incluye dos interfaces opcionales basadas en el código
original:

- **Aplicación de escritorio** (`vault_complete.py`), construida con
  CustomTkinter. Permite temas oscuros, sincronización y auditoría.
- **Aplicación móvil** (`mobile_vault.py`), basada en Kivy y adaptada a
  pantallas táctiles.

Para ejecutarlas, instala las dependencias correspondientes e inicia los
scripts desde la carpeta del proyecto.

## Notas de diseño

- **Cifrado simplificado**: se usa una función XOR con un flujo
  pseudoaleatorio derivado de SHA-256. No es tan robusto como AES-GCM,
  pero permite ocultar la información sin dependencias externas.
- **Persistencia del *salt***: al guardar la bóveda se reutiliza la sal
  original, manteniendo la validez de la clave derivada.
- **Separación de lógica y UI**: la lógica de negocio es independiente
  de la interfaz, lo que facilita crear nuevas interfaces.

## Contribuir

Las contribuciones son bienvenidas. Se sugiere integrar algoritmos de
cifrado más robustos (por ejemplo, mediante la librería `cryptography`)
y ampliar las opciones de sincronización y auditoría.

