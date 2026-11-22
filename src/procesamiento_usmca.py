
from pathlib import Path
from src.generador_pdf import generar_reporte_pdf

import pandas as pd

import getpass
from src.repositories.historial_repository import guardar_ejecucion

from src.services.import_service import ImportService

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
from src.utils.logger import obtener_logger


def _procesar_producto_interno(
    numero_parte,
    directorio_base,
    archivo_aduanas=None,
    archivo_finanzas=None,
    plantilla_excel=None,
    datos_precargados=None,
    productos_preagrupados=None,
    guardar_historial=True,
):
    """
    Procesa un producto terminado y genera su
    hoja de trabajo USMCA.
    """
    logger = obtener_logger()
    base = Path(directorio_base)
    entrada = base / "data" / "input"
    salida = base / "data" / "output"


    # 1. Identificar los archivos de entrada.
    ruta_aduanas = Path(
        archivo_aduanas
        if archivo_aduanas is not None
        else entrada / "P_DISC_BY_EXPORT1.xlsx"
    )

    ruta_finanzas = Path(
        archivo_finanzas
        if archivo_finanzas is not None
        else entrada / "P_Wk_Cost.xlsx"
    )

    ruta_plantilla = Path(
        plantilla_excel
        if plantilla_excel is not None
        else entrada / "P_WORKSHEET.xlsx"
    )

    # Comprobar la existencia de la plantilla.
    if not ruta_plantilla.is_file():
        raise FileNotFoundError(
            "No se encontró la plantilla del reporte "
            "de resultados en Excel."
        )

    # Crear el directorio de salida si no existe.
    salida.mkdir(
        parents=True,
        exist_ok=True
    )

    # Importar una sola vez cuando se procesa por lotes.
    if datos_precargados is None:
        disc = ImportService.cargar_reporte_aduanas(
            ruta_aduanas
        )

        wk_cost = ImportService.cargar_reporte_finanzas(
            ruta_finanzas
        )

        validar_disc_by_export(disc)
        validar_wk_cost(wk_cost)

        logger.info(
            "Archivos de Aduanas y Finanzas "
            "importados y validados correctamente."
        )
    else:
        disc, wk_cost = datos_precargados  

    # 3. Identificar el producto terminado.
    parte = str(numero_parte).strip().upper()

    if productos_preagrupados is None:
        productos = separar_productos(disc)

        encontrados = [
            producto
            for producto in productos
            if str(producto["producto"]).strip().upper()
            == parte
        ]
    else:
        encontrados = productos_preagrupados.get(
            parte, []
        )

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

    logger.info(
        "Consolidación y clasificación completadas. "
        "Producto: %s | Materiales originales: %d | "
        "Materiales consolidados: %d",
        parte,
        len(materiales_originales),
        len(materiales),
    )

    # 6. Obtener costos financieros.
    financieros = obtener_costos_financieros(
        wk_cost, parte
    )

    # 7. Calcular porcentaje no originario.
    resultado = verificar_regla_origen(
        materiales, financieros
    )

    logger.info(
        "Cálculo completado. Producto: %s | "
        "Porcentaje no regional: %.5f%% | "
        "Cumple: %s",
        parte,
        resultado["porcentaje"],
        resultado["cumple"],
    )

    # 8. Generar P_WORKSHEET.
    archivo_salida = salida / f"P_WORKSHEET_{parte}.xlsx"

    generar_worksheet(
        materiales,
        financieros,
        ruta_plantilla,
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

    logger.info(
        "Reportes Excel y PDF generados "
        "correctamente para el producto %s.",
        parte,
    )

    # 9. Preparar el detalle de materiales
    # para guardar la ejecución en el historial.
    detalle_materiales = []

    for _, material in materiales.iterrows():
        costo_no_regional = material["COSTO_I"]

        if pd.isna(costo_no_regional):
            costo_no_regional = 0.0

        detalle_materiales.append({
            "numero_parte": str(material["PARTE"]),
            "descripcion": str(
                material["DESCRIPCION INGLES"]
            ),
            "fraccion_arancelaria": str(
                material["FRACCION MX"]
            ),
            "pais_origen": str(material["ORIGEN"]),
            "es_regional": bool(material["ES_REGIONAL"]),
            "kilogramos": float(
                material["KILOGRAMOS IMPORTACION"]
            ),
            "costo_total": float(material["COSTO_G"]),
            "costo_no_regional": float(
                costo_no_regional
            ),
        })

    # 10. Construir el registro de la ejecución.
    datos_historial = {
        "usuario": getpass.getuser(),
        "archivo_costos": str(ruta_finanzas),
        "archivo_consumos": str(ruta_aduanas),
        "resultados": [
            {
                "numero_parte": parte,
                "total_materiales": resultado[
                    "total_materiales"
                ],
                "labor_day": resultado["labor_day"],
                "indirect_costs": resultado[
                    "indirect_costs"
                ],
                "costo_neto": resultado["costo_neto"],
                "costo_no_originario": resultado[
                    "costo_no_originario"
                ],
                "porcentaje_no_regional": resultado[
                    "porcentaje"
                ],
                "cumple": resultado["cumple"
                ],
                "materiales_originales": len(
                    materiales_originales
                ),
                "materiales_consolidados": len(
                    materiales
                ),
                "archivo_excel": str(archivo_salida),
                "archivo_pdf": str(archivo_pdf),
                "materiales": detalle_materiales,
            }
        ],
    }

    # 11. Registrar individualmente solo si corresponde.
    ejecucion_id = None

    if guardar_historial:
        ejecucion_id = guardar_ejecucion(
            datos_historial,
            ruta_db=base / "database" / "autousmca.db",
        )

        logger.info(
            "Ejecución guardada en SQLite. "
            "ID: %s | Producto: %s",
            ejecucion_id,
            parte,
        )

    return {
        "producto": parte,
        "materiales_originales": len(
            materiales_originales
        ),
        "materiales_consolidados": len(materiales),
        "resultado": resultado,
        "archivo": archivo_salida,
        "archivo_pdf": archivo_pdf,
        "ejecucion_id": ejecucion_id,
        "registro_historial": datos_historial["resultados"][0],
    }

def procesar_producto(
    numero_parte,
    directorio_base,
    archivo_aduanas=None,
    archivo_finanzas=None,
    plantilla_excel=None,
):
    """
    Ejecuta el procesamiento de AutoUSMCA
    y registra sus eventos en la bitácora.
    """

    logger = obtener_logger()
    parte = str(numero_parte).strip().upper()

    logger.info(
        "Inicio del procesamiento. Producto: %s",
        parte,
    )

    try:
        resultado = _procesar_producto_interno(
            numero_parte=numero_parte,
            directorio_base=directorio_base,
            archivo_aduanas=archivo_aduanas,
            archivo_finanzas=archivo_finanzas,
            plantilla_excel=plantilla_excel,
        )

    except Exception:
        logger.exception(
            "Error durante el procesamiento "
            "del producto %s.",
            parte,
        )
        raise

    logger.info(
        "Procesamiento finalizado correctamente. "
        "Producto: %s | Ejecución ID: %s",
        parte,
        resultado["ejecucion_id"],
    )

    return resultado


def procesar_todos_productos(
    directorio_base,
    archivo_aduanas=None,
    archivo_finanzas=None,
    plantilla_excel=None,
    progreso=None,
):
    """
    Procesa cada número de parte único del reporte
    de Aduanas, importando los archivos una sola vez.

    Las apariciones repetidas del mismo producto
    se consolidan en un único resultado.

    Los resultados exitosos se registran en una
    sola ejecución del historial.
    """

    logger = obtener_logger()

    base = Path(directorio_base)
    entrada = base / "data" / "input"

    ruta_aduanas = Path(
        archivo_aduanas
        if archivo_aduanas is not None
        else entrada / "P_DISC_BY_EXPORT1.xlsx"
    )

    ruta_finanzas = Path(
        archivo_finanzas
        if archivo_finanzas is not None
        else entrada / "P_Wk_Cost.xlsx"
    )

    ruta_plantilla = Path(
        plantilla_excel
        if plantilla_excel is not None
        else entrada / "P_WORKSHEET.xlsx"
    )

    if not ruta_plantilla.is_file():
        raise FileNotFoundError(
            "No se encontró la plantilla de resultados Excel."
        )

    logger.info(
        "Inicio del procesamiento masivo."
    )

    try:
        # Importar y validar los archivos una sola vez.
        disc = ImportService.cargar_reporte_aduanas(
            ruta_aduanas
        )

        wk_cost = ImportService.cargar_reporte_finanzas(
            ruta_finanzas
        )

        validar_disc_by_export(disc)
        validar_wk_cost(wk_cost)

        # Identificar las apariciones de productos.
        apariciones = separar_productos(disc)

        # Agrupar por número de parte normalizado.
        # El diccionario conserva el orden de aparición.
        grupos = {}

        for producto in apariciones:
            parte = str(
                producto["producto"]
            ).strip().upper()

            if not parte:
                raise ValueError(
                    "Se encontró un producto sin número de parte."
                )

            grupos.setdefault(parte, []).append(
                producto
            )

        total = len(grupos)

        if total == 0:
            raise ValueError(
                "No se encontraron productos terminados."
            )

        duplicados = len(apariciones) - total

        logger.info(
            "Productos únicos: %d | "
            "Apariciones adicionales agrupadas: %d",
            total,
            duplicados,
        )

        resultados_historial = []
        errores = []

        cumplen = 0
        no_cumplen = 0

        # Procesar una sola vez cada número de parte.
        for indice, parte in enumerate(grupos, start=1):
            try:
                datos = _procesar_producto_interno(
                    numero_parte=parte,
                    directorio_base=base,
                    archivo_aduanas=ruta_aduanas,
                    archivo_finanzas=ruta_finanzas,
                    plantilla_excel=ruta_plantilla,
                    datos_precargados=(disc, wk_cost),
                    productos_preagrupados=grupos,
                    guardar_historial=False,
                )

                resultados_historial.append(
                    datos["registro_historial"]
                )

                if datos["resultado"]["cumple"]:
                    cumplen += 1
                else:
                    no_cumplen += 1

                logger.info(
                    "Producto %s procesado correctamente. "
                    "Avance: %d/%d",
                    parte,
                    indice,
                    total,
                )

            except Exception as error:
                errores.append({
                    "producto": parte,
                    "error": str(error),
                })

                logger.exception(
                    "Error al procesar el producto %s.",
                    parte,
                )

            # Notificar avance, incluso si hubo un error.
            if progreso is not None:
                try:
                    progreso(indice, total, parte)
                except Exception:
                    logger.exception(
                        "Error al comunicar el progreso."
                    )

        procesados = len(resultados_historial)

        if procesados == 0:
            raise RuntimeError(
                "Ningún producto pudo procesarse. "
                "Revise la bitácora de errores."
            )

        # Guardar todos los resultados exitosos
        # dentro de una sola ejecución SQLite.
        datos_historial = {
            "usuario": getpass.getuser(),
            "archivo_costos": str(ruta_finanzas),
            "archivo_consumos": str(ruta_aduanas),
            "resultados": resultados_historial,
        }

        ejecucion_id = guardar_ejecucion(
            datos_historial,
            ruta_db=base / "database" / "autousmca.db",
        )

        logger.info(
            "Procesamiento masivo finalizado. "
            "ID: %s | Productos únicos: %d | "
            "Procesados: %d | Cumplen: %d | "
            "No cumplen: %d | Errores: %d",
            ejecucion_id,
            total,
            procesados,
            cumplen,
            no_cumplen,
            len(errores),
        )

        return {
            "total_productos": total,
            "apariciones_duplicadas": duplicados,
            "procesados": procesados,
            "cumplen": cumplen,
            "no_cumplen": no_cumplen,
            "errores": errores,
            "ejecucion_id": ejecucion_id,
            "directorio_salida": base / "data" / "output",
        }

    except Exception:
        logger.exception(
            "Error general del procesamiento masivo."
        )
        raise
