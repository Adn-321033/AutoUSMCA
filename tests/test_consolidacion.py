
import pandas as pd

from src.consolidacion import (
    separar_productos,
    consolidar_materiales
)


def crear_datos():
    return pd.DataFrame([
        {
            "TIPO": 1,
            "PARTE": "CT0143",
            "DESCRIPCION INGLES": "PRODUCTO",
            "FRACCION MX": "",
            "ORIGEN": "MEX",
            "VALOR US": 0,
            "KILOGRAMOS IMPORTACION": 0
        },
        {
            "TIPO": 2,
            "PARTE": "MAT001",
            "DESCRIPCION INGLES": "TELA",
            "FRACCION MX": "6001",
            "ORIGEN": "CHN",
            "VALOR US": 2.50,
            "KILOGRAMOS IMPORTACION": 0.20
        },
        {
            "TIPO": 2,
            "PARTE": "MAT001",
            "DESCRIPCION INGLES": "TELA",
            "FRACCION MX": "6001",
            "ORIGEN": "CHN",
            "VALOR US": 1.50,
            "KILOGRAMOS IMPORTACION": 0.10
        },
        {
            "TIPO": 1,
            "PARTE": "CT0200",
            "DESCRIPCION INGLES": "PRODUCTO",
            "FRACCION MX": "",
            "ORIGEN": "MEX",
            "VALOR US": 0,
            "KILOGRAMOS IMPORTACION": 0
        },
        {
            "TIPO": 2,
            "PARTE": "MAT002",
            "DESCRIPCION INGLES": "HILO",
            "FRACCION MX": "5204",
            "ORIGEN": "USA",
            "VALOR US": 0.80,
            "KILOGRAMOS IMPORTACION": 0.05
        }
    ])


def test_separar_dos_productos():
    productos = separar_productos(crear_datos())

    assert len(productos) == 2
    assert productos[0]["producto"] == "CT0143"
    assert productos[1]["producto"] == "CT0200"


def test_materiales_por_producto():
    productos = separar_productos(crear_datos())

    assert len(productos[0]["materiales"]) == 2
    assert len(productos[1]["materiales"]) == 1


def test_consolidar_material_repetido():
    productos = separar_productos(crear_datos())

    materiales = consolidar_materiales(
        productos[0]["materiales"]
    )

    assert len(materiales) == 1
    assert abs(materiales.iloc[0]["VALOR US"] - 4.0) < 1e-9
    assert abs(
        materiales.iloc[0]["KILOGRAMOS IMPORTACION"] - 0.30
    ) < 1e-9


from pathlib import Path


def test_consolidacion_archivo_real():
    ruta = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "input"
        / "P_DISC_BY_EXPORT1.xlsx"
    )

    df = pd.read_excel(ruta, dtype={"PARTE": str})

    productos = separar_productos(df)

    assert len(productos) > 0

    primer_producto = productos[0]

    assert primer_producto["producto"] == "CT0143"

    materiales_originales = primer_producto["materiales"]

    assert len(materiales_originales) == 14

    materiales_consolidados = consolidar_materiales(
        materiales_originales
    )

    assert len(materiales_consolidados) <= 14

    # La consolidación no debe alterar los totales.
    for columna in ["VALOR US", "KILOGRAMOS IMPORTACION"]:
        total_original = pd.to_numeric(
            materiales_originales[columna]
        ).sum()

        total_consolidado = materiales_consolidados[
            columna
        ].sum()

        assert abs(
            total_original - total_consolidado
        ) < 1e-8
