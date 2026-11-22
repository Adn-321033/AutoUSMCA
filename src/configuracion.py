
import json
import math
import unicodedata
from pathlib import Path
from src.rutas import RUTA_CONFIGURACION
from src.seguridad_umbral import verificar_contrasena
from src.utils.logger import obtener_logger

PAISES_REGIONALES = {"MEX", "USA", "CAN"}

EQUIVALENCIAS_PREDETERMINADAS = {
    "MEX": "MEX",
    "MX": "MEX",
    "MEXICO": "MEX",
    "USA": "USA",
    "US": "USA",
    "UNITED STATES": "USA",
    "ESTADOS UNIDOS": "USA",
    "CAN": "CAN",
    "CA": "CAN",
    "CANADA": "CAN",
}


def normalizar_texto(valor):
    """
    Normaliza nombres de países eliminando
    espacios adicionales, acentos y diferencias
    entre mayúsculas y minúsculas.
    """
    if not isinstance(valor, str):
        raise ValueError("El país debe ser texto.")

    texto = " ".join(valor.strip().upper().split())

    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    return texto


def configuracion_predeterminada():
    """
    Devuelve los parámetros iniciales
    de AutoUSMCA.
    """
    return {
        "umbral_porcentaje": 10.0,
        "equivalencias_paises": (
            EQUIVALENCIAS_PREDETERMINADAS.copy()
        ),
    }


def validar_configuracion(configuracion):
    """
    Comprueba que el umbral y el catálogo
    tengan valores válidos.
    """
    if not isinstance(configuracion, dict):
        raise ValueError(
            "La configuración debe ser un diccionario."
        )

    if "umbral_porcentaje" not in configuracion:
        raise ValueError(
            "Falta el umbral de cumplimiento."
        )

    umbral = configuracion["umbral_porcentaje"]

    if isinstance(umbral, bool) or not isinstance(
        umbral, (int, float)
    ):
        raise ValueError(
            "El umbral debe ser un valor numérico."
        )

    if not math.isfinite(umbral) or not 0 <= umbral <= 100:
        raise ValueError(
            "El umbral debe estar entre 0 y 100."
        )

    equivalencias = configuracion.get(
        "equivalencias_paises"
    )

    if not isinstance(equivalencias, dict):
        raise ValueError(
            "El catálogo de países debe ser un diccionario."
        )

    catalogo = {}

    for nombre, codigo in equivalencias.items():
        clave = normalizar_texto(nombre)
        valor = normalizar_texto(codigo)

        if not clave:
            raise ValueError(
                "No se permiten países vacíos."
            )

        if len(valor) != 3 or not valor.isalpha():
            raise ValueError(
                f"Código de país inválido: {codigo}"
            )

        if clave in catalogo and catalogo[clave] != valor:
            raise ValueError(
                f"Equivalencia duplicada: {nombre}"
            )

        catalogo[clave] = valor

    # Evitar que un código regional se reclasifique
    # mediante una equivalencia incorrecta.
    for codigo in PAISES_REGIONALES:
        if catalogo.get(codigo, codigo) != codigo:
            raise ValueError(
                f"No se puede modificar el código {codigo}."
            )

    return {
        "umbral_porcentaje": float(umbral),
        "equivalencias_paises": catalogo,
    }


def cargar_configuracion(ruta=None):
    """
    Carga los parámetros desde un archivo JSON.

    Si todavía no existe, utiliza los valores
    predeterminados del proyecto.
    """
    archivo = (
        Path(ruta)
        if ruta is not None
        else RUTA_CONFIGURACION
    )

    if not archivo.exists():
        return configuracion_predeterminada()

    try:
        with archivo.open(
            "r", encoding="utf-8"
        ) as contenido:
            datos = json.load(contenido)

    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(
            f"No se pudo leer la configuración: {error}"
        ) from error

    return validar_configuracion(datos)



def guardar_configuracion(
    configuracion,
    ruta=None,
    contrasena_umbral=None,
):
    """
    Valida y guarda la configuración.

    Cuando cambia el umbral del archivo principal,
    exige la contraseña administrativa.
    """
    datos = validar_configuracion(configuracion)

    archivo = (
        Path(ruta)
        if ruta is not None
        else RUTA_CONFIGURACION
    )

    archivo = archivo.resolve()

    # Proteger la configuración principal de AutoUSMCA.
    es_configuracion_principal = (
        archivo == RUTA_CONFIGURACION.resolve()
    )

    umbral_anterior = None
    cambio_umbral = False

    if es_configuracion_principal:
        anterior = cargar_configuracion(archivo)

        umbral_anterior = anterior["umbral_porcentaje"]
        umbral_nuevo = datos["umbral_porcentaje"]

        cambio_umbral = umbral_anterior != umbral_nuevo

        if cambio_umbral:
            if not verificar_contrasena(contrasena_umbral):
                obtener_logger().warning(
                    "Intento de modificación de umbral "
                    "sin autorización."
                )

                raise PermissionError(
                    "Contraseña administrativa incorrecta."
                )

    archivo.parent.mkdir(
        parents=True, exist_ok=True
    )

    temporal = archivo.with_name(
        archivo.name + ".tmp"
    )

    try:
        with temporal.open(
            "w", encoding="utf-8"
        ) as contenido:
            json.dump(
                datos,
                contenido,
                indent=4,
                ensure_ascii=False,
            )

        temporal.replace(archivo)

    finally:
        if temporal.exists():
            temporal.unlink()

    if cambio_umbral:
        obtener_logger().info(
            "Cambio de umbral autorizado. "
            "Valor anterior: %.5f%% | "
            "Valor nuevo: %.5f%%",
            umbral_anterior,
            datos["umbral_porcentaje"],
        )

    return archivo

def normalizar_pais(pais, configuracion=None):
    """
    Convierte una variante de país a su código
    de tres letras.

    Los códigos desconocidos de tres letras
    se conservan como no regionales.
    """
    if configuracion is None:
        configuracion = cargar_configuracion()

    datos = validar_configuracion(configuracion)
    clave = normalizar_texto(pais)

    equivalencias = datos["equivalencias_paises"]

    if clave in equivalencias:
        return equivalencias[clave]

    if len(clave) == 3 and clave.isalpha():
        return clave

    raise ValueError(
        f"País de origen no reconocido: {pais}"
    )
