# Gestor de Contraseñas Profesional – Refactor

Este proyecto es una refactorización del **Gestor de Contraseñas Profesional**.
Su objetivo principal es ofrecer una arquitectura ordenada y modular, con
componentes probados individualmente.  El código está escrito y
comentado en español para facilitar la comprensión y el mantenimiento.

## Características principales

- **Cifrado de datos** mediante una clave derivada a partir de una
  contraseña maestra.  Los datos de la bóveda se almacenan en disco
  cifrados; al abrir la bóveda se solicita la contraseña para poder
  descifrarlos.
- **Generación de contraseñas seguras** con longitud y tipos de
  caracteres configurables.
- **Evaluación de fortaleza de contraseñas**, proporcionando un
  puntaje simple y recomendaciones de mejora.
- **Sincronización local** simulada que permite subir, descargar y
  sincronizar la bóveda en una carpeta que actúa como “nube”.  Esta
  implementación no requiere acceso a Internet.
- **Auditoría de seguridad** que detecta contraseñas débiles y
  duplicadas, y genera un informe con recomendaciones.
- **CLI interactiva** para crear, abrir y gestionar la bóveda desde la
  línea de comandos.
- **Gestión de usuarios e inicio de sesión**: se pueden crear
  usuarios con sus propias credenciales y cada uno tendrá su propia
  bóveda independiente, protegida por una contraseña maestra.

## Gestión de usuarios e inicio de sesión

El módulo ``auth.py`` permite registrar usuarios y validar sus
credenciales de acceso.  Se utiliza el algoritmo ``PBKDF2-HMAC-SHA256``
con una sal aleatoria por usuario para derivar hashes de las
contraseñas de inicio de sesión, dificultando ataques de fuerza bruta.

El flujo básico de autenticación es el siguiente:

1. El usuario introduce su nombre de usuario y contraseña de acceso.
   Si el usuario no existe, se le ofrece la posibilidad de
   registrarse.
2. Tras iniciar sesión, se solicita una contraseña maestra para
   cifrar/descifrar la bóveda.  Esta contraseña puede ser la misma que
   la de acceso o diferente, según preferencia del usuario.
3. La bóveda se almacena en un archivo cuyo nombre por defecto es
   ``<usuario>_vault.json``.  Cada usuario tiene así su propia
   bóveda, aislada de las demás.

Esta separación entre credenciales de acceso y clave maestra refuerza
la seguridad y permite gestionar múltiples usuarios en un mismo
sistema.

## Estructura del código

```
refactored_vault/
│
├── password_vault/       # Paquete principal de la aplicación
│   ├── __init__.py       # Expone las funciones y clases públicas
│   ├── core.py           # Cifrado/descifrado y gestión de archivo
│   ├── password_utils.py # Generación y evaluación de contraseñas
│   ├── cloud.py          # Sincronización local de la bóveda
│   ├── audit.py          # Auditoría de seguridad y portapapeles seguro
│   ├── auth.py           # Gestión de usuarios e inicio de sesión
│   └── cli.py            # Interfaz de línea de comandos con login
│
├── tests/                # Conjunto de pruebas unitarias
│   ├── test_core.py
│   ├── test_password_utils.py
│   ├── test_cloud.py
│   ├── test_audit.py
│   └── test_auth.py
└── README.md             # Este documento
```

Cada módulo está diseñado para cumplir una única responsabilidad y
contiene documentación clara. Las pruebas unitarias verifican el
comportamiento esperado de cada componente.

## Requisitos

* Python 3.10 o superior.
* No se necesitan dependencias externas para ejecutar la línea de comandos;
  todas las bibliotecas usadas pertenecen a la librería estándar de Python.
* **Para ejecutar las interfaces gráficas** necesitas instalar
  adicionalmente las bibliotecas `customtkinter` (para la app de
  escritorio) y `kivy` (para la app móvil).  Estas librerías no se
  incluyen por defecto y deben instalarse manualmente, por ejemplo
  mediante `pip install customtkinter kivy`.

## Instalación

1. Clona este repositorio o descarga el paquete ZIP y descomprímelo.
2. Navega hasta la carpeta `refactored_vault`.
3. (Opcional) Crea un entorno virtual: `python -m venv venv && source venv/bin/activate`.
4. No es necesario instalar dependencias externas.

## Uso

Para utilizar la interfaz de línea de comandos con gestión de
usuarios, ejecuta:

```bash
python -m password_vault.cli
```

El programa iniciará solicitando el nombre de usuario y la
contraseña de acceso.  Si el usuario no existe, se te preguntará si
deseas registrarlo.  Una vez autenticado, tendrás que proporcionar
una contraseña maestra para cifrar tu bóveda; esta puede ser la misma
o distinta de la de acceso.  El archivo de la bóveda se llamará por
defecto ``<usuario>_vault.json``, aunque puedes indicar otra ruta.

A continuación podrás añadir, listar y eliminar entradas, así como
ejecutar una auditoría de seguridad.

Ejemplo de flujo:

```
Gestor de Contraseñas CLI
==============================
Ruta del archivo de usuarios [users.json]:
Nombre de usuario: alice
Contraseña: ********
Usuario no encontrado. ¿Desea registrarse? [s/N]: s
Usuario registrado correctamente.
Contraseña maestra de la bóveda: ********
Ruta del archivo de la bóveda [alice_vault.json]:

Opciones:
1) Listar entradas
2) Agregar entrada
3) Eliminar entrada
4) Auditoría de seguridad
5) Guardar y salir
```

## Pruebas

Las pruebas unitarias se encuentran en el directorio `tests`.  Para
ejecutarlas utiliza el módulo `unittest` de la librería estándar:

```bash
cd refactored_vault
python -m unittest discover -s tests -v
```

Esto ejecutará todas las pruebas y mostrará un resumen del resultado.

## Interfaz gráfica (escritorio y móvil)

Además de la CLI, el proyecto incluye dos interfaces gráficas basadas
en el código original: una aplicación de escritorio construida con
**CustomTkinter** y una aplicación móvil construida con **Kivy**.  No
se ha modificado la apariencia ni el flujo de estas aplicaciones; se
han adaptado únicamente las importaciones para que funcionen con la
arquitectura refactorizada.

### Aplicación de escritorio (`vault_complete.py`)

Este script proporciona una interfaz moderna con temas oscuros, auto‑
bloqueo, sincronización y auditoría de seguridad.  Para ejecutarla:

```bash
cd refactored_vault
python vault_complete.py
```

Aparecerá una ventana con un campo para la contraseña maestra.  Si es
la primera vez, se creará automáticamente la bóveda y se almacenará
en el archivo `password_vault_complete.json` en el mismo directorio.
Los datos se sincronizan en la carpeta `vault_cloud_complete/` cuando
eliges la opción de sincronizar.  El resto de funcionalidades (añadir,
editar, eliminar entradas y auditoría) se mantienen igual que en el
proyecto original.

### Aplicación móvil (`mobile_vault.py`)

La versión móvil simula una pantalla de 360×640 píxeles y ofrece un
flujo similar adaptado a pantallas táctiles.  Para ejecutarla:

```bash
cd refactored_vault
python mobile_vault.py
```

La app abrirá una ventana con la interfaz móvil.  Necesitarás tener
`kivy` instalado.  La bóveda se guarda en `mobile_vault.json` y se
sincroniza en la carpeta `mobile_cloud/`.  Todas las operaciones
(login, sincronizar, añadir/editar entradas) conservan la misma
experiencia que el código original.

## Notas de diseño

* **Cifrado simplificado**: Debido a que el entorno no permite instalar
  dependencias como `cryptography`, el cifrado se implementa mediante
  una función XOR con un flujo pseudoaleatorio generado a partir de
  SHA‑256. Aunque no es tan robusto como AES‑GCM, cumple el propósito
  de ocultar la información y permitir la refactorización del código.
* **Persistencia del salt**: Al guardar la bóveda se reutiliza la
  sal original, de modo que la clave derivada siga siendo válida.
* **Independencia de UI**: La lógica de negocio se mantiene
  completamente separada de la interfaz de usuario. La clase de la
  interfaz CLI es un ejemplo de cómo consumir la API proporcionada.

## Contribución

Se anima a mejorar este proyecto incorporando algoritmos de cifrado
más robustos (por ejemplo, integrando `cryptography` cuando sea
posible) y ampliando las funcionalidades de sincronización y auditoría.
