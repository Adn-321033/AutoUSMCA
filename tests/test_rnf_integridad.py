
import hashlib
from pathlib import Path

import pytest

from src.procesamiento_usmca import procesar_producto


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = BASE_DIR / "data" / "input"


def calcular_hash(ruta):
    """Calcula el SHA-256 de un archivo."""
    sha256 = hashlib.sha256()

    with open(ruta, "rb") as archivo:
        for bloque in iter(
            lambda: archivo.read(1024 * 1024), b""
        ):
            sha256.update(bloque)

    return sha256.hexdigest()


def test_archivos_originales_no_modificados():
    """
    RNF-10:
    El procesamiento no debe modificar
    los archivos originales.
    """
    archivos = [
        INPUT_DIR / "P_DISC_BY_EXPORT1.xlsx",
        INPUT_DIR / "P_Wk_Cost.xlsx",
        INPUT_DIR / "P_WORKSHEET.xlsx",
    ]

    for archivo in archivos:
        assert archivo.is_file(), (
            f"No se encontró: {archivo.name}"
        )

    hashes_antes = {
        archivo.name: calcular_hash(archivo)
        for archivo in archivos
    }

    procesar_producto("CT0143", BASE_DIR)

    hashes_despues = {
        archivo.name: calcular_hash(archivo)
        for archivo in archivos
    }

    assert hashes_antes == hashes_despues

    print(
        "\nRNF-10 APROBADO:"
        " los archivos originales no se modificaron."
    )


def test_resultados_reproducibles():
    """
    RNF-14:
    Los mismos datos de entrada deben producir
    los mismos resultados de cálculo.
    """
    primera = procesar_producto(
        "CT0143", BASE_DIR
    )

    segunda = procesar_producto(
        "CT0143", BASE_DIR
    )

    calculo_1 = primera["resultado"]
    calculo_2 = segunda["resultado"]

    campos = [
        "total_materiales",
        "labor_day",
        "indirect_costs",
        "costo_neto",
        "costo_no_originario",
        "proporcion",
        "porcentaje",
    ]

    for campo in campos:
        assert calculo_1[campo] == pytest.approx(
            calculo_2[campo],
            rel=0,
            abs=1e-12,
        ), f"Resultado diferente: {campo}"

    assert (
        calculo_1["cumple"] == calculo_2["cumple"]
    )

    assert (
        primera["materiales_consolidados"]
        == segunda["materiales_consolidados"]
    )

    print(
        "\nRNF-14 APROBADO:"
        " resultados consistentes."
    )
