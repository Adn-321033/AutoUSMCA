
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

from src.generador_excel import generar_worksheet


BASE_DIR = Path(__file__).resolve().parent.parent
PLANTILLA = BASE_DIR / "data" / "input" / "P_WORKSHEET.xlsx"
SALIDAS = BASE_DIR / "data" / "output"


def crear_materiales(cantidad):
    return pd.DataFrame([
        {
            "PARTE": f"MAT{i:03d}",
            "DESCRIPCION INGLES": f"MATERIAL {i}",
            "FRACCION MX": "6001000000",
            "ORIGEN": "CHN" if i % 2 else "MEX",
            "COSTO_F": 1.50,
            "COSTO_G": 1.50,
            "COSTO_H": 1.50 if i % 2 == 0 else None,
            "COSTO_I": 1.50 if i % 2 else None,
            "KILOGRAMOS IMPORTACION": 0.025
        }
        for i in range(1, cantidad + 1)
    ])


def crear_financieros():
    return {
        "labor_day": 2.50,
        "indirect_costs": 1.75
    }


def test_generar_worksheet_14_materiales():
    ruta = SALIDAS / "prueba_14_materiales.xlsx"

    generar_worksheet(
        crear_materiales(14),
        crear_financieros(),
        PLANTILLA,
        ruta
    )

    wb = load_workbook(ruta)
    ws = wb["Hoja1"]

    assert ws["A3"].value == 1
    assert ws["B3"].value == "MAT001"
    assert ws["J3"].value == 0.025

    assert ws["G21"].value == 2.50
    assert ws["G22"].value == 1.75

    assert ws["G23"].value == "=SUM(G3:G22)"
    assert ws["F26"].value == "=IFERROR(I23/G23,0)"
    assert ws["G26"].value == "=F26"

    wb.close()


def test_generar_worksheet_22_materiales():
    ruta = SALIDAS / "prueba_22_materiales.xlsx"

    generar_worksheet(
        crear_materiales(22),
        crear_financieros(),
        PLANTILLA,
        ruta
    )

    wb = load_workbook(ruta)
    ws = wb["Hoja1"]

    assert ws["A24"].value == 22
    assert ws["B24"].value == "MAT022"

    assert ws["G25"].value == 2.50
    assert ws["G26"].value == 1.75

    assert ws["G27"].value == "=SUM(G3:G26)"
    assert ws["F30"].value == "=IFERROR(I27/G27,0)"
    assert ws["G30"].value == "=F30"

    # Se conservan los otros apartados del libro.
    assert len(wb.worksheets) == 3

    wb.close()
