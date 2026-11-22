
from pathlib import Path

import pandas as pd
import pytest

from src.validacion import validar_columnas_requeridas


# Ruta principal del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "test"

COLUMNAS_REQUERIDAS = [
    "OPERACION",
    "NUMERO_PARTE",
    "PAIS_ORIGEN",
    "COSTO_NETO"
]


def test_excel_correcto():
    ruta = DATA_DIR / "archivo_correcto.xlsx"

    # Leer el archivo Excel real
    df = pd.read_excel(ruta)

    # Validar las columnas
    resultado = validar_columnas_requeridas(
        df, COLUMNAS_REQUERIDAS
    )

    assert resultado is True


def test_excel_incompleto():
    ruta = DATA_DIR / "archivo_incompleto.xlsx"

    # Leer el archivo Excel real
    df = pd.read_excel(ruta)

    # Comprobar que detecta la columna faltante
    with pytest.raises(ValueError, match="PAIS_ORIGEN"):
        validar_columnas_requeridas(
            df, COLUMNAS_REQUERIDAS
        )
