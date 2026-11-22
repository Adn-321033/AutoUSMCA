
import pandas as pd

from src.validacion import validar_columnas_requeridas


# Columnas necesarias del archivo de materiales.
COLUMNAS_DISC = [
    "TIPO",
    "OPERACION",
    "PARTE",
    "FRACCION MX",
    "ORIGEN",
    "VALOR US",
    "KILOGRAMOS IMPORTACION",
    "DESCRIPCION INGLES",
]


def validar_disc_by_export(df):
    """
    Valida la estructura básica del reporte de materiales.
    """

    validar_columnas_requeridas(df, COLUMNAS_DISC)

    if df.empty:
        raise ValueError(
            "P_DISC_BY_EXPORT1 no contiene registros."
        )

    tipos = pd.to_numeric(df["TIPO"], errors="coerce")

    if tipos.isna().any():
        raise ValueError(
            "La columna TIPO contiene valores no numéricos o vacíos."
        )

    if not tipos.isin([1, 2]).all():
        raise ValueError(
            "TIPO solo puede contener los valores 1 y 2."
        )

    if not (tipos == 1).any():
        raise ValueError(
            "No se encontraron facturas de exportación."
        )

    if tipos.iloc[0] != 1:
        raise ValueError(
            "El primer registro debe ser una factura de exportación."
        )

    operaciones = df["OPERACION"].astype("string").str.strip().str.casefold()

    correspondencia = (
        ((tipos == 1) & (operaciones == "factura exportacion"))
        | ((tipos == 2) & (operaciones.isin([
            "descargo importacion",
            "descargos importacion"
        ])))
    )

    if not correspondencia.all():
        raise ValueError(
            "Existen inconsistencias entre TIPO y OPERACION."
        )

    if df["PARTE"].isna().any():
        raise ValueError(
            "Existen registros sin número de parte."
        )

    materiales = df.loc[tipos == 2]

    if materiales.empty:
        raise ValueError(
            "No se encontraron materiales de importación."
        )

    if materiales["ORIGEN"].isna().any():
        raise ValueError(
            "Existen materiales sin país de origen."
        )

    origenes = materiales["ORIGEN"].astype("string").str.strip()

    if not origenes.str.fullmatch(r"[A-Za-z]{3}").all():
        raise ValueError(
            "Los países de origen deben tener tres letras."
        )

    for columna in ["VALOR US", "KILOGRAMOS IMPORTACION"]:
        valores = pd.to_numeric(
            materiales[columna], errors="coerce"
        )

        if valores.isna().any() or (valores < 0).any():
            raise ValueError(
                f"La columna {columna} contiene valores inválidos."
            )

    return True


def validar_wk_cost(df):
    """
    Valida las posiciones requeridas del reporte financiero.

    El DataFrame debe leerse con header=None.
    La fila 4 de Excel corresponde al índice 3.
    """

    if df.empty:
        raise ValueError(
            "P_Wk_Cost está vacío."
        )

    # Columna B hasta columna O.
    if df.shape[1] < 15:
        raise ValueError(
            "P_Wk_Cost debe contener al menos 15 columnas."
        )

    # Debe existir al menos un registro a partir de fila 4.
    if len(df) < 4:
        raise ValueError(
            "P_Wk_Cost no contiene registros de productos."
        )

    productos = df.iloc[3:]

    if productos.iloc[:, 1].isna().all():
        raise ValueError(
            "No se encontraron números de parte en la columna B."
        )

    return True
