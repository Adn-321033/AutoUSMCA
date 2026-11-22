
from pathlib import Path
from src.generador_pdf import generar_reporte_pdf

import pandas as pd

from src.validacion_archivos import (
    validar_disc_by_export,
    validar_wk_cost,
)
from src.consolidacion import (
    separar_productos,
    consolidar_materiales,
)
from src.clasificacion import clasificar_materiales
from src.motor_calculo import obtener_costos_financieros
from src.regla_origen import verificar_regla_origen
from src.generador_excel import generar_worksheet


def procesar_producto(numero_parte, directorio_base):
    """
    Procesa un producto terminado y genera su
    hoja de trabajo USMCA.
    """

    base = Path(directorio_base)
    entrada = base / "data" / "input"
    salida = base / "data" / "output"

    # 1. Leer archivos originales.
    disc = pd.read_excel(
        entrada / "P_DISC_BY_EXPORT1.xlsx",
        dtype={"PARTE": str, "FRACCION MX": str}
    )

    wk_cost = pd.read_excel(
        entrada / "P_Wk_Cost.xlsx",
        header=None
    )

    # 2. Validar archivos.
    validar_disc_by_export(disc)
    validar_wk_cost(wk_cost)

    # 3. Identificar el producto terminado.
    productos = separar_productos(disc)

    parte = str(numero_parte).strip().upper()

    encontrados = [
        producto for producto in productos
        if producto["producto"].upper() == parte
    ]

    if not encontrados:
        raise ValueError(
            f"No se encontró el producto {parte}."
        )

    # 4. Consolidar materiales del producto.
    # Si el mismo producto aparece en varias exportaciones,
    # reunimos sus materiales para esta prueba.
    materiales_originales = pd.concat(
        [p["materiales"] for p in encontrados],
        ignore_index=True
    )

    materiales = consolidar_materiales(
        materiales_originales
    )

    # 5. Clasificar costos por origen.
    materiales = clasificar_materiales(materiales)

    # 6. Obtener costos financieros.
    financieros = obtener_costos_financieros(
        wk_cost, parte
    )

    # 7. Calcular porcentaje no originario.
    resultado = verificar_regla_origen(
        materiales, financieros
    )

    # 8. Generar P_WORKSHEET.
    archivo_salida = salida / f"P_WORKSHEET_{parte}.xlsx"

    generar_worksheet(
        materiales,
        financieros,
        entrada / "P_WORKSHEET.xlsx",
        archivo_salida
    )

    archivo_pdf = salida / f"REPORTE_USMCA_{parte}.pdf"

    generar_reporte_pdf(
        producto=parte,
        materiales=materiales,
        financieros=financieros,
        resultado=resultado,
        ruta_salida=archivo_pdf,
        materiales_originales=len(materiales_originales),
    )

    return {
        "producto": parte,
        "materiales_originales": len(materiales_originales),
        "materiales_consolidados": len(materiales),
        "resultado": resultado,
        "archivo": archivo_salida,
        "archivo_pdf": archivo_pdf,
    }
