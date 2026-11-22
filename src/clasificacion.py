
import pandas as pd


PAISES_REGIONALES = {"MEX", "USA", "CAN"}


def clasificar_materiales(df):
    """
    Clasifica los materiales según su país de origen.

    Regionales: MEX, USA, CAN.
    No regionales: los demás códigos de tres letras.

    Prepara los costos de las columnas F, G, H e I
    de P_WORKSHEET.
    """

    if df.empty:
        return df.copy()

    resultado = df.copy()

    columnas = ["ORIGEN", "VALOR US"]

    faltantes = [
        columna for columna in columnas
        if columna not in resultado.columns
    ]

    if faltantes:
        raise ValueError(
            f"Columnas faltantes: {faltantes}"
        )

    resultado["ORIGEN"] = (
        resultado["ORIGEN"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    origen_valido = resultado["ORIGEN"].str.fullmatch(
        r"[A-Z]{3}"
    ).fillna(False)

    if not origen_valido.all():
        raise ValueError(
            "Se encontraron códigos de origen inválidos."
        )

    resultado["VALOR US"] = pd.to_numeric(
        resultado["VALOR US"],
        errors="coerce"
    )

    if (
        resultado["VALOR US"].isna().any()
        or (resultado["VALOR US"] < 0).any()
    ):
        raise ValueError(
            "Se encontraron costos inválidos."
        )

    resultado["ES_REGIONAL"] = (
        resultado["ORIGEN"].isin(PAISES_REGIONALES)
    )

    resultado["COSTO_F"] = resultado["VALOR US"]
    resultado["COSTO_G"] = resultado["VALOR US"]

    resultado["COSTO_H"] = resultado["VALOR US"].where(
        resultado["ES_REGIONAL"]
    )

    resultado["COSTO_I"] = resultado["VALOR US"].where(
        ~resultado["ES_REGIONAL"]
    )

    return resultado
