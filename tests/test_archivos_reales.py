
from pathlib import Path

import pandas as pd

from src.validacion_archivos import (
    validar_disc_by_export,
    validar_wk_cost,
)


BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "input"


def test_disc_real():
    ruta = INPUT_DIR / "P_DISC_BY_EXPORT1.XLSX"

    df = pd.read_excel(ruta)

    assert validar_disc_by_export(df) is True


def test_wk_cost_real():
    ruta = INPUT_DIR / "P_Wk_Cost.xlsx"

    df = pd.read_excel(ruta, header=None)

    assert validar_wk_cost(df) is True
