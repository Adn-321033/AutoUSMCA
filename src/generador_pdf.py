
from pathlib import Path
from xml.sax.saxutils import escape
import math

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)


def generar_reporte_pdf(
    producto,
    materiales,
    financieros,
    resultado,
    ruta_salida,
    materiales_originales=None,
):
    """
    Genera un reporte PDF complementario
    con los resultados del cálculo USMCA.
    """

    if materiales.empty:
        raise ValueError("No existen materiales para el PDF.")

    columnas = [
        "PARTE",
        "ORIGEN",
        "VALOR US",
        "COSTO_I",
        "KILOGRAMOS IMPORTACION",
    ]

    faltantes = [
        c for c in columnas
        if c not in materiales.columns
    ]

    if faltantes:
        raise ValueError(f"Faltan columnas: {faltantes}")

    campos = [
        "total_materiales",
        "costo_neto",
        "costo_no_originario",
        "porcentaje",
    ]

    if any(c not in resultado for c in campos):
        raise ValueError("Faltan resultados del cálculo.")

    def numero(valor):
        try:
            n = float(valor)
        except (ValueError, TypeError):
            raise ValueError("Valor numérico inválido.") from None

        if not math.isfinite(n):
            raise ValueError("Se encontraron valores no finitos.")

        return n

    def formato(valor):
        return f"{numero(valor):,.5f}"

    ruta = Path(ruta_salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)

    documento = SimpleDocTemplate(
        str(ruta),
        pagesize=landscape(A4),
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    estilos = getSampleStyleSheet()

    estilos.add(ParagraphStyle(
        name="TituloUSMCA",
        parent=estilos["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17365D"),
        fontSize=16,
        spaceAfter=12,
    ))

    estilos.add(ParagraphStyle(
        name="CeldaUSMCA",
        parent=estilos["Normal"],
        fontSize=8,
        leading=10,
    ))

    elementos = []

    elementos.append(Paragraph(
        "AUTOUSMCA - REPORTE DE CONTENIDO REGIONAL",
        estilos["TituloUSMCA"],
    ))

    elementos.append(Paragraph(
        f"<b>Producto terminado:</b> "
        f"{escape(str(producto))}",
        estilos["Normal"],
    ))

    elementos.append(Paragraph(
        f"<b>Materiales consolidados:</b> "
        f"{len(materiales)}",
        estilos["Normal"],
    ))

    if materiales_originales is not None:
        elementos.append(Paragraph(
            f"<b>Registros originales:</b> "
            f"{materiales_originales}",
            estilos["Normal"],
        ))

    elementos.append(Spacer(1, 12))

    # Resumen financiero.
    elementos.append(Paragraph(
        "<b>1. Resumen financiero</b>",
        estilos["Heading2"],
    ))

    resumen = [
        ["Concepto", "Importe USD"],
        ["Costo de materiales",
         formato(resultado["total_materiales"])],
        ["Labor Day",
         formato(financieros["labor_day"])],
        ["Indirect Costs",
         formato(financieros["indirect_costs"])],
        ["Costo neto total",
         formato(resultado["costo_neto"])],
        ["Costo no originario",
         formato(resultado["costo_no_originario"])],
    ]

    tabla_resumen = Table(
        resumen,
        colWidths=[115 * mm, 45 * mm],
        hAlign="LEFT",
    )

    tabla_resumen.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),
         colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
    ]))

    elementos.append(tabla_resumen)
    elementos.append(Spacer(1, 14))

    # Resultado del porcentaje.
    elementos.append(Paragraph(
        "<b>2. Resultado del cálculo</b>",
        estilos["Heading2"],
    ))

    porcentaje = numero(resultado["porcentaje"])

    elementos.append(Paragraph(
        f"<b>Porcentaje no originario:</b> "
        f"{porcentaje:.5f}%",
        estilos["Normal"],
    ))

    dentro = porcentaje <= 10.0 + 1e-10

    comparacion = (
        "Dentro del umbral de referencia del 10%"
        if dentro
        else "Por encima del umbral de referencia del 10%"
    )

    elementos.append(Paragraph(
        f"<b>Comparación:</b> {comparacion}",
        estilos["Normal"],
    ))

    elementos.append(Spacer(1, 12))

    # Detalle de materiales.
    elementos.append(Paragraph(
        "<b>3. Detalle de materiales</b>",
        estilos["Heading2"],
    ))

    detalle = [[
        "Número de parte",
        "Origen",
        "Costo USD",
        "No originario USD",
        "Peso kg",
    ]]

    for _, material in materiales.iterrows():
        costo_i = material["COSTO_I"]

        if pd.isna(costo_i):
            costo_i = 0.0

        detalle.append([
            escape(str(material["PARTE"])),
            escape(str(material["ORIGEN"])),
            formato(material["VALOR US"]),
            formato(costo_i),
            formato(material["KILOGRAMOS IMPORTACION"]),
        ])

    tabla_detalle = Table(
        detalle,
        colWidths=[55 * mm, 30 * mm, 45 * mm,
                   52 * mm, 40 * mm],
        repeatRows=1,
        hAlign="LEFT",
    )

    tabla_detalle.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),
         colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
    ]))

    elementos.append(tabla_detalle)
    elementos.append(Spacer(1, 12))

    elementos.append(Paragraph(
        "<b>Nota:</b> Reporte de apoyo generado por "
        "AutoUSMCA. El porcentaje se calcula con los "
        "datos proporcionados. La comparación con el "
        "10% es informativa y no constituye por sí sola "
        "una certificación de origen T-MEC.",
        estilos["CeldaUSMCA"],
    ))

    documento.build(elementos)

    return ruta
