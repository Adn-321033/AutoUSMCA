import pandas as pd
import pytest

from src.validacion import validar_columnas_requeridas

COLUMNAS_REQUERIDAS = [
    "OPERACION",
    "NUMERO_PARTE",
    "PAIS_ORIGEN",
    "COSTO_NETO"
]

def test_columnas_requeridas_presentes():

    df = pd.DataFrame(
        columns=[
            "OPERACION",
            "NUMERO_PARTE",
            "PAIS_ORIGEN",
            "COSTO_NETO"
        ]
    )

    resultado = validar_columnas_requeridas(
        df,
        COLUMNAS_REQUERIDAS
    )

    assert resultado is True

def test_columna_requerida_faltante():

    df = pd.DataFrame(
        columns=[
            "OPERACION",
            "NUMERO_PARTE",
            "COSTO_NETO"
        ]
    )

    with pytest.raises(
        ValueError,
        match="PAIS_ORIGEN"
    ):
        validar_columnas_requeridas(
            df,
            COLUMNAS_REQUERIDAS
        )

