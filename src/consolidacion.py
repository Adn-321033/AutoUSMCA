
import pandas as pd


def separar_productos(df):
    """
    Separa los productos terminados y sus materiales.

    TIPO = 1: producto terminado.
    TIPO = 2: material del producto anterior.
    """

    productos = []
    producto_actual = None
    materiales = []

    for _, fila in df.iterrows():
        tipo = int(fila["TIPO"])

        if tipo == 1:
            if producto_actual is not None:
                productos.append({
                    "producto": producto_actual,
                    "materiales": pd.DataFrame(materiales)
                })

            producto_actual = str(fila["PARTE"]).strip()
            materiales = []

        elif tipo == 2:
            if producto_actual is None:
                raise ValueError(
                    "Material encontrado sin producto terminado."
                )

            materiales.append(fila.to_dict())

        else:
            raise ValueError(
                f"Tipo de operación no válido: {tipo}"
            )

    if producto_actual is not None:
        productos.append({
            "producto": producto_actual,
            "materiales": pd.DataFrame(materiales)
        })

    return productos


def consolidar_materiales(df):
    """
    Agrupa registros del mismo material y suma
    costos y kilogramos.

    Conserva separados los registros cuando
    cambian origen, fracción o descripción.
    """

    if df.empty:
        return df.copy()

    columnas_agrupacion = [
        "PARTE",
        "DESCRIPCION INGLES",
        "FRACCION MX",
        "ORIGEN"
    ]

    resultado = df.copy()

    for columna in ["VALOR US", "KILOGRAMOS IMPORTACION"]:
        resultado[columna] = pd.to_numeric(
            resultado[columna],
            errors="raise"
        )

    resultado = (
        resultado.groupby(
            columnas_agrupacion,
            as_index=False,
            sort=False,
            dropna=False
        )[["VALOR US", "KILOGRAMOS IMPORTACION"]]
        .sum()
    )

    return resultado
