
import getpass
import hashlib
import hmac
import json
import secrets
from pathlib import Path

from src.rutas import RUTA_SEGURIDAD_UMBRAL

RUTA_SEGURIDAD = RUTA_SEGURIDAD_UMBRAL

ITERACIONES = 600_000


def seguridad_configurada(ruta=None):
    """Comprueba si existe la contraseña administrativa."""
    archivo = Path(ruta) if ruta is not None else RUTA_SEGURIDAD
    return archivo.is_file()


def crear_contrasena(contrasena, ruta=None):
    """
    Crea la contraseña administrativa inicial.

    La contraseña nunca se guarda en texto plano.
    """
    archivo = Path(ruta) if ruta is not None else RUTA_SEGURIDAD

    if archivo.exists():
        raise ValueError(
            "Ya existe una contraseña administrativa. "
            "No se permite reemplazarla mediante "
            "la inicialización."
        )

    if not isinstance(contrasena, str) or len(contrasena) < 12:
        raise ValueError(
            "La contraseña debe tener al menos 12 caracteres."
        )

    sal = secrets.token_bytes(16)

    derivado = hashlib.pbkdf2_hmac(
        "sha256",
        contrasena.encode("utf-8"),
        sal,
        ITERACIONES,
    )

    datos = {
        "algoritmo": "pbkdf2_sha256",
        "iteraciones": ITERACIONES,
        "sal": sal.hex(),
        "hash": derivado.hex(),
    }

    archivo.parent.mkdir(parents=True, exist_ok=True)

    # La creación exclusiva impide sobrescribir
    # una contraseña que ya exista.
    with archivo.open("x", encoding="utf-8") as contenido:
        json.dump(datos, contenido, indent=4)

    return archivo


def verificar_contrasena(contrasena, ruta=None):
    """
    Verifica la contraseña administrativa.

    Si la configuración de seguridad no existe
    o está dañada, no autoriza la modificación.
    """
    archivo = Path(ruta) if ruta is not None else RUTA_SEGURIDAD

    if not archivo.is_file():
        raise ValueError(
            "No existe una contraseña administrativa. "
            "Primero debe inicializar la seguridad."
        )

    try:
        with archivo.open("r", encoding="utf-8") as contenido:
            datos = json.load(contenido)

        if datos["algoritmo"] != "pbkdf2_sha256":
            raise ValueError("Algoritmo no reconocido.")

        iteraciones = datos["iteraciones"]

        if (
            type(iteraciones) is not int
            or not 100_000 <= iteraciones <= 2_000_000
        ):
            raise ValueError("Número de iteraciones inválido.")

        sal = bytes.fromhex(datos["sal"])
        hash_guardado = bytes.fromhex(datos["hash"])

        if len(sal) != 16 or len(hash_guardado) != 32:
            raise ValueError("Datos de seguridad inválidos.")

    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ValueError(
            "No fue posible validar la configuración "
            "de seguridad administrativa."
        ) from error

    if not isinstance(contrasena, str):
        return False

    hash_calculado = hashlib.pbkdf2_hmac(
        "sha256",
        contrasena.encode("utf-8"),
        sal,
        iteraciones,
    )

    return hmac.compare_digest(
        hash_calculado,
        hash_guardado,
    )


def inicializar_seguridad():
    """Solicita la contraseña desde la consola."""
    if seguridad_configurada():
        print(
            "La seguridad administrativa ya está configurada."
        )
        return

    print("CONFIGURACIÓN INICIAL DE SEGURIDAD")
    print("La contraseña debe tener al menos 12 caracteres.")

    primera = getpass.getpass(
        "Nueva contraseña administrativa: "
    )

    segunda = getpass.getpass(
        "Confirmar contraseña: "
    )

    if primera != segunda:
        raise ValueError(
            "Las contraseñas no coinciden."
        )

    ruta = crear_contrasena(primera)

    print(
        f"Seguridad administrativa configurada en: {ruta}"
    )


if __name__ == "__main__":
    try:
        inicializar_seguridad()
    except ValueError as error:
        print(f"Error: {error}")
        raise SystemExit(1) from None
