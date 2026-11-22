
import time
from pathlib import Path

import pandas as pd
import pytest

from src.generador_excel import generar_worksheet
from src.generador_pdf import generar_reporte_pdf


BASE_DIR = Path(__file__).resolve().parents[1]
PLANTILLA = BASE_DIR / "data" / "input" / "P_WORKSHEET.xlsx"

CANTIDAD_PRODUCTOS = 500
MATERIALES_POR_PRODUCTO = 14


def crear_datos_prueba():
    """
    Crea 14 materiales sintéticos reutilizables
    para medir la generación de reportes.
    """

    origenes = [
        ["MEX", "USA", "CAN", "CHN"][i % 4]
        for i in range(MATERIALES_POR_PRODUCTO)
    ]

    costos_no_originarios = [
        0.10 if origen == "CHN" else 0.0
        for origen in origenes
    ]

    materiales = pd.DataFrame({
        "PARTE": [
            f"MAT{i:05d}"
            for i in range(MATERIALES_POR_PRODUCTO)
        ],
        "DESCRIPCION INGLES": [
            f"Material sintético {i}"
            for i in range(MATERIALES_POR_PRODUCTO)
        ],
        "FRACCION MX": [
            "39269099"
        ] * MATERIALES_POR_PRODUCTO,
        "ORIGEN": origenes,
        "VALOR US": [1.0] * MATERIALES_POR_PRODUCTO,
        "COSTO_F": [1.0] * MATERIALES_POR_PRODUCTO,
        "COSTO_G": [1.0] * MATERIALES_POR_PRODUCTO,
        "COSTO_H": [0.0] * MATERIALES_POR_PRODUCTO,
        "COSTO_I": costos_no_originarios,
        "KILOGRAMOS IMPORTACION": [
            0.10
        ] * MATERIALES_POR_PRODUCTO,
    })

    financieros = {
        "labor_day": 15.0,
        "indirect_costs": 3.0,
    }

    total_materiales = 14.0
    costo_neto = total_materiales + 15.0 + 3.0
    costo_no_originario = sum(costos_no_originarios)
    porcentaje = costo_no_originario / costo_neto * 100

    resultado = {
        "total_materiales": total_materiales,
        "costo_neto": costo_neto,
        "costo_no_originario": costo_no_originario,
        "porcentaje": porcentaje,
        "cumple": porcentaje <= 10.0,
        "umbral_utilizado": 10.0,
    }

    return materiales, financieros, resultado


@pytest.mark.parametrize(
    "formato,limite",
    [
        ("excel", 30.0),
        ("pdf", 60.0),
    ],
)
def test_generacion_500_reportes(tmp_path, formato, limite):
    """
    RNF-03: medición de 500 reportes individuales.

    No modifica los archivos originales.
    """

    materiales, financieros, resultado = (
        crear_datos_prueba()
    )

    if formato == "excel":
        assert PLANTILLA.is_file(), (
            f"No existe la plantilla: {PLANTILLA}"
        )

    inicio = time.perf_counter()

    for numero in range(CANTIDAD_PRODUCTOS):
        producto = f"PROD{numero:05d}"

        if formato == "excel":
            salida = tmp_path / f"{producto}.xlsx"

            generar_worksheet(
                materiales,
                financieros,
                PLANTILLA,
                salida,
            )

        else:
            salida = tmp_path / f"{producto}.pdf"

            generar_reporte_pdf(
                producto,
                materiales,
                financieros,
                resultado,
                salida,
            )

        assert salida.is_file()
        assert salida.stat().st_size > 0

    tiempo = time.perf_counter() - inicio

    print(
        f"\nFormato: {formato.upper()}"
        f"\nProductos: {CANTIDAD_PRODUCTOS}"
        f"\nMateriales por producto: "
        f"{MATERIALES_POR_PRODUCTO}"
        f"\nReportes generados: {CANTIDAD_PRODUCTOS}"
        f"\nTiempo total: {tiempo:.5f} segundos"
        f"\nLímite de referencia: {limite:.2f} segundos"
    )

    assert tiempo <= limite, (
        f"Tiempo de {formato.upper()} superior "
        f"al límite: {tiempo:.5f} segundos"
    )
