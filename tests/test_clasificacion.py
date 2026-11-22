
import pandas as pd
import pytest

from src.clasificacion import clasificar_materiales


@pytest.mark.parametrize(
    "pais",
    ["MEX", "USA", "CAN"]
)
def test_material_regional(pais):
    df = pd.DataFrame({
        "ORIGEN": [pais],
        "VALOR US": [10.50]
    })

    resultado = clasificar_materiales(df)

    assert bool(resultado.iloc[0]["ES_REGIONAL"])
    assert resultado.iloc[0]["COSTO_F"] == 10.50
    assert resultado.iloc[0]["COSTO_G"] == 10.50
    assert resultado.iloc[0]["COSTO_H"] == 10.50
    assert pd.isna(resultado.iloc[0]["COSTO_I"])


def test_material_no_regional():
    df = pd.DataFrame({
        "ORIGEN": ["CHN"],
        "VALOR US": [8.25]
    })

    resultado = clasificar_materiales(df)

    assert not bool(resultado.iloc[0]["ES_REGIONAL"])
    assert pd.isna(resultado.iloc[0]["COSTO_H"])
    assert resultado.iloc[0]["COSTO_I"] == 8.25


def test_pais_invalido():
    df = pd.DataFrame({
        "ORIGEN": ["CHINA"],
        "VALOR US": [5.00]
    })

    with pytest.raises(
        ValueError, match="origen inválidos"
    ):
        clasificar_materiales(df)


def test_costo_invalido():
    df = pd.DataFrame({
        "ORIGEN": ["MEX"],
        "VALOR US": [-10.00]
    })

    with pytest.raises(
        ValueError, match="costos inválidos"
    ):
        clasificar_materiales(df)


def test_conservacion_costos():
    df = pd.DataFrame({
        "ORIGEN": ["MEX", "USA", "CHN"],
        "VALOR US": [10.00, 20.00, 5.00]
    })

    resultado = clasificar_materiales(df)

    total_original = df["VALOR US"].sum()

    total_clasificado = (
        resultado["COSTO_H"].sum()
        + resultado["COSTO_I"].sum()
    )

    assert abs(
        total_original - total_clasificado
    ) < 1e-9


from pathlib import Path

from src.consolidacion import (
    separar_productos,
    consolidar_materiales
)


def test_clasificacion_ct0143_real():
    ruta = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "input"
        / "P_DISC_BY_EXPORT1.xlsx"
    )

    df = pd.read_excel(ruta)

    productos = separar_productos(df)

    ct0143 = next(
        producto for producto in productos
        if producto["producto"] == "CT0143"
    )

    materiales = consolidar_materiales(
        ct0143["materiales"]
    )

    resultado = clasificar_materiales(materiales)

    # Los costos regionales y no regionales
    # deben sumar el costo original.
    total_original = resultado["VALOR US"].sum()

    total_clasificado = (
        resultado["COSTO_H"].sum()
        + resultado["COSTO_I"].sum()
    )

    assert abs(
        total_original - total_clasificado
    ) < 1e-8

    # Ningún registro debe tener costo en H e I
    # simultáneamente.
    assert not (
        resultado["COSTO_H"].notna()
        & resultado["COSTO_I"].notna()
    ).any()
