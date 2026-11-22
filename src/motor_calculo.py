
import pandas as pd


def obtener_costos_financieros(df, numero_parte):
    """
    Busca un producto en P_Wk_Cost y calcula:
      Labor Day: columnas G + H.
      Indirect Costs: columnas I hasta O.

    El DataFrame se lee con header=None.
    """

    if df.shape[1] < 15:
        raise ValueError(
            "P_Wk_Cost no contiene todas las columnas requeridas."
        )

    parte = str(numero_parte).strip().upper()

    # Columna B: índice 1.
    codigos = (
        df.iloc[:, 1]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    coincidencias = df.loc[codigos == parte]

    if coincidencias.empty:
        raise ValueError(
            f"No se encontró el producto {parte} en P_Wk_Cost."
        )

    if len(coincidencias) > 1:
        raise ValueError(
            f"El producto {parte} aparece más de una vez."
        )

    fila = coincidencias.iloc[0]

    # Columnas G hasta O: índices 6 a 14.
    costos = pd.to_numeric(
        fila.iloc[6:15],
        errors="coerce"
    )

    if costos.isna().any():
        raise ValueError(
            f"El producto {parte} contiene costos vacíos "
            "o no numéricos."
        )

    if (costos < 0).any():
        raise ValueError(
            f"El producto {parte} contiene costos negativos."
        )

    labor_day = float(costos.iloc[0:2].sum())
    indirect_costs = float(costos.iloc[2:9].sum())

    return {
        "producto": parte,
        "labor_day": labor_day,
        "indirect_costs": indirect_costs,
        "total_costos": labor_day + indirect_costs
    }
