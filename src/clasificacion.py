
import pandas as pd

from src.configuracion import (
    cargar_configuracion,
    normalizar_pais,
    PAISES_REGIONALES,
)


def clasificar_materiales(df, configuracion=None):
    """
    Clasifica materiales según su país de origen.

    Acepta códigos de tres letras y equivalencias
    definidas en la configuración del sistema.

    Conserva las columnas de costos F, G, H e I.
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

    if configuracion is None:
        configuracion = cargar_configuracion()

    # Normalizar los países utilizando el catálogo.
    resultado["ORIGEN"] = resultado["ORIGEN"].apply(
        lambda pais: normalizar_pais(
            pais, configuracion
        )
    )

    # Validar los costos de los materiales.
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

    # Clasificar materiales regionales.
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
