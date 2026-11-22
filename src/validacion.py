def validar_columnas_requeridas(df, columnas_requeridas):
    columnas_faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in df.columns
    ]

    if columnas_faltantes:
        raise ValueError(
            f"Faltan columnas obligatorias: {', '.join(columnas_faltantes)}"
        )

    return True

    