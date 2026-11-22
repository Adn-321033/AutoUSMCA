
import pandas as pd
import pytest

from src.validacion_archivos import (
    validar_disc_by_export,
    validar_wk_cost,
)


def crear_disc_valido():
    return pd.DataFrame([
        {
            "TIPO": 1,
            "OPERACION": "Factura exportacion",
            "PARTE": "CT0143",
            "FRACCION MX": "6105200301",
            "ORIGEN": "MEX",
            "VALOR US": 9.70,
            "KILOGRAMOS IMPORTACION": 0,
            "DESCRIPCION INGLES": "PRODUCTO TERMINADO",
        },
        {
            "TIPO": 2,
            "OPERACION": "Descargo importacion",
            "PARTE": "C00007",
            "FRACCION MX": "3215199999",
            "ORIGEN": "CHN",
            "VALOR US": 0.004979,
            "KILOGRAMOS IMPORTACION": 0.00026,
            "DESCRIPCION INGLES": "PRINTER INK",
        },
    ])


def test_disc_archivo_correcto():
    df = crear_disc_valido()

    assert validar_disc_by_export(df) is True


def test_disc_columna_faltante():
    df = crear_disc_valido()
    df = df.drop(columns=["ORIGEN"])

    with pytest.raises(ValueError, match="ORIGEN"):
        validar_disc_by_export(df)


def test_disc_tipo_invalido():
    df = crear_disc_valido()
    df.loc[1, "TIPO"] = 3

    with pytest.raises(ValueError, match="TIPO"):
        validar_disc_by_export(df)


def test_disc_pais_invalido():
    df = crear_disc_valido()
    df.loc[1, "ORIGEN"] = "CHINA"

    with pytest.raises(ValueError, match="tres letras"):
        validar_disc_by_export(df)


def test_disc_costo_negativo():
    df = crear_disc_valido()
    df.loc[1, "VALOR US"] = -5

    with pytest.raises(ValueError, match="VALOR US"):
        validar_disc_by_export(df)


def test_wk_cost_archivo_correcto():
    df = pd.DataFrame(
        [[None] * 16 for _ in range(5)]
    )
    df.iloc[3, 1] = "CT0143"

    assert validar_wk_cost(df) is True


def test_wk_cost_columnas_insuficientes():
    df = pd.DataFrame(
        [[None] * 10 for _ in range(5)]
    )

    with pytest.raises(ValueError, match="15 columnas"):
        validar_wk_cost(df)


def test_wk_cost_sin_productos():
    df = pd.DataFrame(
        [[None] * 16 for _ in range(5)]
    )

    with pytest.raises(ValueError, match="números de parte"):
        validar_wk_cost(df)
