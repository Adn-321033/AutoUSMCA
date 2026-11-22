
"""
Administración centralizada de rutas de AutoUSMCA.

Permite utilizar los mismos directorios tanto
durante el desarrollo como al ejecutar la
aplicación empaquetada con PyInstaller.
"""

import sys
from pathlib import Path


def obtener_directorio_base():
    """
    Devuelve la carpeta principal de AutoUSMCA.

    - En desarrollo: carpeta que contiene main.py.
    - En el ejecutable: carpeta que contiene AutoUSMCA.exe.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent.parent


BASE_DIR = obtener_directorio_base()

DIRECTORIO_CONFIG = BASE_DIR / "config"
DIRECTORIO_DATOS = BASE_DIR / "data"
DIRECTORIO_ENTRADA = DIRECTORIO_DATOS / "input"
DIRECTORIO_SALIDA = DIRECTORIO_DATOS / "output"
DIRECTORIO_DATABASE = BASE_DIR / "database"
DIRECTORIO_LOGS = BASE_DIR / "logs"

RUTA_CONFIGURACION = (
    DIRECTORIO_CONFIG / "configuracion.json"
)

RUTA_SEGURIDAD_UMBRAL = (
    DIRECTORIO_CONFIG / "seguridad_umbral.json"
)

RUTA_BASE_DATOS = (
    DIRECTORIO_DATABASE / "autousmca.db"
)

RUTA_LOG = (
    DIRECTORIO_LOGS / "autousmca.log"
)

RUTA_PLANTILLA = (
    DIRECTORIO_ENTRADA / "P_WORKSHEET.xlsx"
)


def preparar_directorios():
    """Crea las carpetas necesarias para operar."""
    for directorio in (
        DIRECTORIO_CONFIG,
        DIRECTORIO_ENTRADA,
        DIRECTORIO_SALIDA,
        DIRECTORIO_DATABASE,
        DIRECTORIO_LOGS,
    ):
        directorio.mkdir(parents=True, exist_ok=True)
