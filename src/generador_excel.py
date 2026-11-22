
from copy import copy
from pathlib import Path

from openpyxl import load_workbook


def generar_worksheet(
    materiales,
    financieros,
    ruta_plantilla,
    ruta_salida
):
    """
    Genera P_WORKSHEET con los materiales clasificados,
    costos financieros, pesos y fórmulas actualizadas.
    """

    if materiales.empty:
        raise ValueError("No existen materiales para el reporte.")

    columnas_requeridas = [
        "PARTE", "DESCRIPCION INGLES", "FRACCION MX",
        "ORIGEN", "COSTO_F", "COSTO_G",
        "COSTO_H", "COSTO_I",
        "KILOGRAMOS IMPORTACION"
    ]

    faltantes = [
        col for col in columnas_requeridas
        if col not in materiales.columns
    ]

    if faltantes:
        raise ValueError(f"Faltan columnas: {faltantes}")

    for clave in ("labor_day", "indirect_costs"):
        if clave not in financieros:
            raise ValueError(f"Falta el costo: {clave}")

    plantilla = Path(ruta_plantilla)
    salida = Path(ruta_salida)

    if not plantilla.is_file():
        raise FileNotFoundError(
            f"No existe la plantilla: {plantilla}"
        )

    wb = load_workbook(plantilla)
    ws = wb["Hoja1"]

    cantidad = len(materiales)
    adicionales = max(0, cantidad - 18)

    # Insertar filas antes de LABOR DAY.
    if adicionales:
        ws.insert_rows(21, amount=adicionales)

        # Copiar el formato de una fila de materiales.
        for fila in range(21, 21 + adicionales):
            ws.row_dimensions[fila].height = (
                ws.row_dimensions[20].height
            )

            for columna in range(1, 11):
                origen = ws.cell(20, columna)
                destino = ws.cell(fila, columna)

                if origen.has_style:
                    destino._style = copy(origen._style)

                destino.alignment = copy(origen.alignment)
                destino.protection = copy(origen.protection)

    # Introducir materiales.
    for indice, (_, material) in enumerate(
        materiales.iterrows(), start=3
    ):
        ws.cell(indice, 1, indice - 2)

        # Códigos tratados como texto para conservar ceros.
        for columna, campo in [
            (2, "PARTE"),
            (3, "DESCRIPCION INGLES"),
            (4, "FRACCION MX"),
            (5, "ORIGEN")
        ]:
            valor = material[campo]

            celda = ws.cell(indice, columna)
            celda.value = "" if str(valor) == "nan" else str(valor)
            celda.number_format = "@"

        # Costos y peso.
        for columna, campo in [
            (6, "COSTO_F"),
            (7, "COSTO_G"),
            (8, "COSTO_H"),
            (9, "COSTO_I"),
            (10, "KILOGRAMOS IMPORTACION")
        ]:
            valor = material[campo]

            if valor is None or valor != valor:
                ws.cell(indice, columna).value = None
            else:
                ws.cell(indice, columna).value = float(valor)

    # Posiciones dinámicas.
    fila_labor = 21 + adicionales
    fila_indirectos = 22 + adicionales
    fila_totales = 23 + adicionales
    fila_porcentaje = 26 + adicionales

    ws.cell(fila_labor, 7).value = float(
        financieros["labor_day"]
    )

    ws.cell(fila_indirectos, 7).value = float(
        financieros["indirect_costs"]
    )

    # Actualizar las fórmulas de la plantilla.
    ultima_fila_costos = fila_indirectos

    for columna in ("G", "H", "I", "J"):
        ws[f"{columna}{fila_totales}"] = (
            f"=SUM({columna}3:"
            f"{columna}{ultima_fila_costos})"
        )

    ws[f"F{fila_porcentaje}"] = (
        f"=IFERROR(I{fila_totales}/G{fila_totales},0)"
    )

    ws[f"G{fila_porcentaje}"] = (
        f"=F{fila_porcentaje}"
    )

    # Mostrar el resultado como porcentaje.
    ws[f"F{fila_porcentaje}"].number_format = "0.00000%"
    ws[f"G{fila_porcentaje}"].number_format = "0.00000%"

    # Solicitar recálculo al abrir en Excel.
    wb.calculation.fullCalcOnLoad = True
    wb.calculation.forceFullCalc = True
    wb.calculation.calcMode = "auto"

    salida.parent.mkdir(parents=True, exist_ok=True)
    wb.save(salida)

    return salida
