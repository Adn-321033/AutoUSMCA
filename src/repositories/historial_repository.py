
from datetime import datetime

from src.repositories.database import (
    crear_base_datos,
    obtener_conexion,
)


def guardar_ejecucion(datos, ruta_db=None):
    """
    Guarda una ejecución completa, sus resultados
    y el detalle de materiales.

    La operación es transaccional: si ocurre un error,
    no se guarda información incompleta.
    """

    crear_base_datos(ruta_db)
    conexion = obtener_conexion(ruta_db)

    try:
        resultados = datos["resultados"]

        if not resultados:
            raise ValueError(
                "La ejecución debe contener al menos un resultado."
            )

        cumple = sum(
            1 for r in resultados if r["cumple"]
        )

        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO ejecuciones (
                fecha_ejecucion,
                usuario,
                archivo_costos,
                archivo_consumos,
                total_partes,
                partes_cumplen,
                partes_no_cumplen,
                estado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(
                    sep=" ", timespec="seconds"
                ),
                datos.get("usuario", "Usuario local"),
                datos.get("archivo_costos", ""),
                datos.get("archivo_consumos", ""),
                len(resultados),
                cumple,
                len(resultados) - cumple,
                "FINALIZADA",
            ),
        )

        ejecucion_id = cursor.lastrowid

        for resultado in resultados:

            cursor.execute(
                """
                INSERT INTO resultados (
                    ejecucion_id,
                    numero_parte,
                    total_materiales,
                    labor_day,
                    indirect_costs,
                    costo_neto,
                    costo_no_originario,
                    porcentaje_no_regional,
                    cumple,
                    cantidad_materiales_originales,
                    cantidad_materiales_consolidados,
                    archivo_excel,
                    archivo_pdf
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ejecucion_id,
                    resultado["numero_parte"],
                    resultado["total_materiales"],
                    resultado["labor_day"],
                    resultado["indirect_costs"],
                    resultado["costo_neto"],
                    resultado["costo_no_originario"],
                    resultado["porcentaje_no_regional"],
                    int(resultado["cumple"]),
                    resultado.get("materiales_originales"),
                    resultado.get("materiales_consolidados"),
                    str(resultado.get("archivo_excel", "")),
                    str(resultado.get("archivo_pdf", "")),
                ),
            )

            resultado_id = cursor.lastrowid

            for material in resultado.get("materiales", []):

                cursor.execute(
                    """
                    INSERT INTO detalle_materiales (
                        resultado_id,
                        numero_parte,
                        descripcion,
                        fraccion_arancelaria,
                        pais_origen,
                        es_regional,
                        kilogramos,
                        costo_total,
                        costo_no_regional
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        resultado_id,
                        str(material["numero_parte"]),
                        material.get("descripcion"),
                        material.get("fraccion_arancelaria"),
                        material["pais_origen"],
                        int(material["es_regional"]),
                        material["kilogramos"],
                        material["costo_total"],
                        material["costo_no_regional"],
                    ),
                )

        conexion.commit()
        return ejecucion_id

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def consultar_ejecuciones(
    fecha_desde=None,
    fecha_hasta=None,
    usuario=None,
    numero_parte=None,
    ruta_db=None,
):
    """
    Consulta ejecuciones usando filtros opcionales.
    """

    crear_base_datos(ruta_db)
    conexion = obtener_conexion(ruta_db)

    try:
        consulta = """
            SELECT DISTINCT e.*
            FROM ejecuciones e
            WHERE 1 = 1
        """

        parametros = []

        if fecha_desde:
            consulta += " AND date(e.fecha_ejecucion) >= date(?)"
            parametros.append(fecha_desde)

        if fecha_hasta:
            consulta += " AND date(e.fecha_ejecucion) <= date(?)"
            parametros.append(fecha_hasta)

        if usuario:
            consulta += " AND e.usuario LIKE ?"
            parametros.append(f"%{usuario}%")

        if numero_parte:
            consulta += """
                AND EXISTS (
                    SELECT 1
                    FROM resultados r
                    WHERE r.ejecucion_id = e.id
                    AND r.numero_parte = ?
                )
            """
            parametros.append(
                str(numero_parte).strip().upper()
            )

        consulta += """
            ORDER BY e.fecha_ejecucion DESC, e.id DESC
        """

        filas = conexion.execute(
            consulta, parametros
        ).fetchall()

        return [dict(fila) for fila in filas]

    finally:
        conexion.close()


def obtener_ejecucion(ejecucion_id, ruta_db=None):
    """
    Recupera una ejecución con sus resultados
    y materiales, sin recalcular los datos.
    """

    crear_base_datos(ruta_db)
    conexion = obtener_conexion(ruta_db)

    try:
        fila = conexion.execute(
            "SELECT * FROM ejecuciones WHERE id = ?",
            (ejecucion_id,),
        ).fetchone()

        if fila is None:
            return None

        ejecucion = dict(fila)

        resultados = conexion.execute(
            """
            SELECT *
            FROM resultados
            WHERE ejecucion_id = ?
            ORDER BY id
            """,
            (ejecucion_id,),
        ).fetchall()

        ejecucion["resultados"] = []

        for fila_resultado in resultados:
            resultado = dict(fila_resultado)

            materiales = conexion.execute(
                """
                SELECT *
                FROM detalle_materiales
                WHERE resultado_id = ?
                ORDER BY id
                """,
                (resultado["id"],),
            ).fetchall()

            resultado["materiales"] = [
                dict(material) for material in materiales
            ]

            ejecucion["resultados"].append(resultado)

        return ejecucion

    finally:
        conexion.close()
