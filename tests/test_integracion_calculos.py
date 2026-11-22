
from pathlib import Path

import pandas as pd
import pytest

from src.validacion_archivos import (
    validar_disc_by_export,
    validar_wk_cost,
)
from src.consolidacion import (
    separar_productos,
    consolidar_materiales,
)
from src.clasificacion import clasificar_materiales
from src.motor_calculo import obtener_costos_financieros


BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "input"


@pytest.fixture
def datos_ct0143():
    """Prepara los datos reales del producto CT0143."""

    disc = pd.read_excel(
        INPUT_DIR / "P_DISC_BY_EXPORT1.xlsx"
    )

    wk_cost = pd.read_excel(
        INPUT_DIR / "P_Wk_Cost.xlsx",
        header=None
    )

    assert validar_disc_by_export(disc) is True
    assert validar_wk_cost(wk_cost) is True

    productos = separar_productos(disc)

    producto = next(
        (p for p in productos if p["producto"] == "CT0143"),
        None
    )

    assert producto is not None

    originales = producto["materiales"]
    consolidados = consolidar_materiales(originales)
    clasificados = clasificar_materiales(consolidados)

    financieros = obtener_costos_financieros(
        wk_cost, "CT0143"
    )

    return {
        "originales": originales,
        "consolidados": consolidados,
        "clasificados": clasificados,
        "financieros": financieros,
        "wk_cost": wk_cost
    }


def test_integracion_productos_materiales(datos_ct0143):
    """Comprueba que CT0143 conserva sus 14 materiales."""

    assert len(datos_ct0143["originales"]) == 14

    assert 0 < len(datos_ct0143["consolidados"]) <= 14


def test_integracion_conservacion_costos(datos_ct0143):
    """El total de materiales no debe alterarse."""

    originales = datos_ct0143["originales"]
    clasificados = datos_ct0143["clasificados"]

    costo_original = pd.to_numeric(
        originales["VALOR US"]
    ).sum()

    costo_final = clasificados["COSTO_G"].sum()

    assert costo_final == pytest.approx(
        costo_original, abs=1e-8
    )


def test_integracion_conservacion_pesos(datos_ct0143):
    """Comprueba que no se pierdan kilogramos."""

    originales = datos_ct0143["originales"]
    consolidados = datos_ct0143["consolidados"]

    peso_original = pd.to_numeric(
        originales["KILOGRAMOS IMPORTACION"]
    ).sum()

    peso_final = consolidados[
        "KILOGRAMOS IMPORTACION"
    ].sum()

    assert peso_final == pytest.approx(
        peso_original, abs=1e-8
    )


def test_integracion_clasificacion(datos_ct0143):
    """El total regional y no regional debe cuadrar."""

    df = datos_ct0143["clasificados"]

    total = df["VALOR US"].sum()

    regional = df["COSTO_H"].sum()
    no_regional = df["COSTO_I"].sum()

    assert regional + no_regional == pytest.approx(
        total, abs=1e-8
    )

    assert not (
        df["COSTO_H"].notna()
        & df["COSTO_I"].notna()
    ).any()


def test_integracion_costos_financieros(datos_ct0143):
    """Compara costos financieros con la fila 45."""

    df = datos_ct0143["wk_cost"]
    resultado = datos_ct0143["financieros"]

    fila = pd.to_numeric(df.iloc[44, 6:15])

    assert resultado["labor_day"] == pytest.approx(
        fila.iloc[0:2].sum()
    )

    assert resultado["indirect_costs"] == pytest.approx(
        fila.iloc[2:9].sum()
    )


def test_integracion_total_preliminar(datos_ct0143):
    """Comprueba el total de materiales y fabricación."""

    materiales = datos_ct0143["clasificados"]
    financieros = datos_ct0143["financieros"]

    total_materiales = materiales["COSTO_G"].sum()

    total_fabricacion = (
        financieros["labor_day"]
        + financieros["indirect_costs"]
    )

    total_preliminar = (
        total_materiales + total_fabricacion
    )

    assert total_preliminar == pytest.approx(
        materiales["VALOR US"].sum()
        + financieros["total_costos"]
    )

    assert total_preliminar >= 0
