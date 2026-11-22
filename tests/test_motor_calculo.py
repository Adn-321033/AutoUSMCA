
import pandas as pd
import pytest

from src.motor_calculo import obtener_costos_financieros


def crear_datos_financieros():
    df = pd.DataFrame(
        [[None] * 15 for _ in range(5)]
    )

    df.iloc[4, 1] = "CT0143"

    # G y H: mano de obra.
    df.iloc[4, 6] = 2.00
    df.iloc[4, 7] = 1.50

    # I hasta O: siete costos indirectos.
    for columna in range(8, 15):
        df.iloc[4, columna] = 0.50

    return df


def test_calculo_labor_day():
    resultado = obtener_costos_financieros(
        crear_datos_financieros(), "CT0143"
    )

    assert resultado["labor_day"] == pytest.approx(3.50)


def test_calculo_indirect_costs():
    resultado = obtener_costos_financieros(
        crear_datos_financieros(), "CT0143"
    )

    assert resultado["indirect_costs"] == pytest.approx(3.50)


def test_total_costos():
    resultado = obtener_costos_financieros(
        crear_datos_financieros(), "CT0143"
    )

    assert resultado["total_costos"] == pytest.approx(7.00)


def test_producto_no_encontrado():
    with pytest.raises(ValueError, match="No se encontró"):
        obtener_costos_financieros(
            crear_datos_financieros(), "CT9999"
        )


def test_costo_invalido():
    df = crear_datos_financieros()
    df.iloc[4, 6] = "INVALIDO"

    with pytest.raises(ValueError, match="no numéricos"):
        obtener_costos_financieros(df, "CT0143")


def test_producto_duplicado():
    df = crear_datos_financieros()
    duplicado = df.iloc[[4]].copy()
    df = pd.concat([df, duplicado], ignore_index=True)

    with pytest.raises(ValueError, match="más de una vez"):
        obtener_costos_financieros(df, "CT0143")


from pathlib import Path


def test_costos_ct0143_real():
    ruta = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "input"
        / "P_Wk_Cost.xlsx"
    )

    df = pd.read_excel(ruta, header=None)

    resultado = obtener_costos_financieros(
        df, "CT0143"
    )

    # Referencia manual: fila 45 de Excel.
    fila_45 = pd.to_numeric(
        df.iloc[44, 6:15],
        errors="raise"
    )

    labor_esperado = float(fila_45.iloc[0:2].sum())
    indirecto_esperado = float(fila_45.iloc[2:9].sum())

    assert str(df.iloc[44, 1]).strip().upper() == "CT0143"

    assert resultado["labor_day"] == pytest.approx(
        labor_esperado
    )

    assert resultado["indirect_costs"] == pytest.approx(
        indirecto_esperado
    )
