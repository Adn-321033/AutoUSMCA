
import pandas as pd
import pytest

from src.regla_origen import verificar_regla_origen


def crear_materiales(no_originario=10.0):
    return pd.DataFrame({
        "COSTO_G": [50.0, 30.0],
        "COSTO_I": [no_originario, float("nan")]
    })


def crear_financieros():
    return {
        "labor_day": 10.0,
        "indirect_costs": 10.0
    }


@pytest.mark.parametrize(
    "costo_no_originario, porcentaje_esperado, dentro",
    [
        (5.0, 5.0, True),
        (10.0, 10.0, True),
        (20.0, 20.0, False),
        (0.0, 0.0, True),
    ]
)
def test_porcentajes(
    costo_no_originario,
    porcentaje_esperado,
    dentro
):
    resultado = verificar_regla_origen(
        crear_materiales(costo_no_originario),
        crear_financieros()
    )

    assert resultado["porcentaje"] == pytest.approx(
        porcentaje_esperado
    )
    assert resultado["dentro_umbral_10"] is dentro


def test_costo_neto():
    resultado = verificar_regla_origen(
        crear_materiales(), crear_financieros()
    )

    assert resultado["costo_neto"] == pytest.approx(100.0)
    assert resultado["costo_no_originario"] == pytest.approx(10.0)


def test_costo_neto_cero():
    materiales = pd.DataFrame({
        "COSTO_G": [0.0],
        "COSTO_I": [0.0]
    })

    financieros = {
        "labor_day": 0.0,
        "indirect_costs": 0.0
    }

    with pytest.raises(ValueError, match="mayor que cero"):
        verificar_regla_origen(materiales, financieros)


from pathlib import Path

from src.consolidacion import (
    separar_productos,
    consolidar_materiales
)
from src.clasificacion import clasificar_materiales
from src.motor_calculo import obtener_costos_financieros


def test_porcentaje_ct0143_real():
    entrada = (
        Path(__file__).resolve().parent.parent
        / "data" / "input"
    )

    disc = pd.read_excel(
        entrada / "P_DISC_BY_EXPORT1.xlsx"
    )

    wk_cost = pd.read_excel(
        entrada / "P_Wk_Cost.xlsx",
        header=None
    )

    productos = separar_productos(disc)

    ct0143 = next(
        p for p in productos
        if p["producto"] == "CT0143"
    )

    materiales = clasificar_materiales(
        consolidar_materiales(ct0143["materiales"])
    )

    financieros = obtener_costos_financieros(
        wk_cost, "CT0143"
    )

    resultado = verificar_regla_origen(
        materiales, financieros
    )

    # Comparación independiente de los totales.
    total_g = (
        materiales["COSTO_G"].sum()
        + financieros["labor_day"]
        + financieros["indirect_costs"]
    )

    total_i = materiales["COSTO_I"].sum()

    assert resultado["proporcion"] == pytest.approx(
        total_i / total_g
    )

    assert 0 <= resultado["porcentaje"] <= 100

    print(
        f"\nCT0143 | Costo neto: {resultado['costo_neto']:.5f}"
        f" | No originario: {resultado['costo_no_originario']:.5f}"
        f" | Porcentaje: {resultado['porcentaje']:.5f}%"
    )


def test_umbral_configurable():
    import pandas as pd

    from src.configuracion import configuracion_predeterminada
    from src.regla_origen import verificar_regla_origen

    materiales = pd.DataFrame({
        "COSTO_G": [90.0, 10.0],
        "COSTO_I": [float("nan"), 10.0],
    })

    financieros = {
        "labor_day": 0.0,
        "indirect_costs": 0.0,
    }

    config = configuracion_predeterminada()

    # Escenario 1: umbral del 10 %
    config["umbral_porcentaje"] = 10.0

    resultado_10 = verificar_regla_origen(
        materiales, financieros, configuracion=config
    )

    assert resultado_10["porcentaje"] == 10.0
    assert resultado_10["cumple"] is True

    # Escenario 2: umbral del 5 %
    config["umbral_porcentaje"] = 5.0

    resultado_5 = verificar_regla_origen(
        materiales, financieros, configuracion=config
    )

    assert resultado_5["porcentaje"] == 10.0
    assert resultado_5["cumple"] is False

    # El cálculo debe mantenerse idéntico.
    assert (
        resultado_10["costo_neto"]
        == resultado_5["costo_neto"]
    )

    assert (
        resultado_10["costo_no_originario"]
        == resultado_5["costo_no_originario"]
    )
