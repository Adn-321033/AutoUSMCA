
import sqlite3

import pytest

from src.repositories.historial_repository import (
    guardar_ejecucion,
    consultar_ejecuciones,
    obtener_ejecucion,
)


@pytest.fixture
def ruta_db(tmp_path):
    """Crea una base de datos temporal para cada prueba."""
    return tmp_path / "historial_pruebas.db"


@pytest.fixture
def datos_ejecucion():
    """Datos controlados para validar el historial."""
    return {
        "usuario": "Pruebas AutoUSMCA",
        "archivo_costos": "reporte_finanzas.xlsx",
        "archivo_consumos": "reporte_aduanas.xlsx",
        "resultados": [
            {
                "numero_parte": "CT0143",
                "total_materiales": 100.0,
                "labor_day": 20.0,
                "indirect_costs": 30.0,
                "costo_neto": 150.0,
                "costo_no_originario": 10.0,
                "porcentaje_no_regional": 6.66667,
                "cumple": True,
                "materiales_originales": 2,
                "materiales_consolidados": 2,
                "archivo_excel": "resultado.xlsx",
                "archivo_pdf": "resultado.pdf",
                "materiales": [
                    {
                        "numero_parte": "MAT001",
                        "descripcion": "Material regional",
                        "fraccion_arancelaria": "1234",
                        "pais_origen": "MEX",
                        "es_regional": True,
                        "kilogramos": 2.5,
                        "costo_total": 90.0,
                        "costo_no_regional": 0.0,
                    },
                    {
                        "numero_parte": "MAT002",
                        "descripcion": "Material no regional",
                        "fraccion_arancelaria": "5678",
                        "pais_origen": "CHN",
                        "es_regional": False,
                        "kilogramos": 1.5,
                        "costo_total": 10.0,
                        "costo_no_regional": 10.0,
                    },
                ],
            }
        ],
    }


def test_guardar_ejecucion(
    ruta_db, datos_ejecucion
):
    ejecucion_id = guardar_ejecucion(
        datos_ejecucion, ruta_db
    )

    assert ejecucion_id == 1

    ejecucion = obtener_ejecucion(
        ejecucion_id, ruta_db
    )

    assert ejecucion["total_partes"] == 1
    assert ejecucion["partes_cumplen"] == 1
    assert ejecucion["partes_no_cumplen"] == 0
    assert len(ejecucion["resultados"]) == 1


def test_recuperar_materiales(
    ruta_db, datos_ejecucion
):
    ejecucion_id = guardar_ejecucion(
        datos_ejecucion, ruta_db
    )

    ejecucion = obtener_ejecucion(
        ejecucion_id, ruta_db
    )

    resultado = ejecucion["resultados"][0]

    assert resultado["numero_parte"] == "CT0143"
    assert resultado["porcentaje_no_regional"] == pytest.approx(
        6.66667
    )

    assert len(resultado["materiales"]) == 2
    assert resultado["materiales"][1]["pais_origen"] == "CHN"


def test_consultar_por_numero_parte(
    ruta_db, datos_ejecucion
):
    guardar_ejecucion(datos_ejecucion, ruta_db)

    registros = consultar_ejecuciones(
        numero_parte="CT0143",
        ruta_db=ruta_db,
    )

    assert len(registros) == 1

    sin_coincidencias = consultar_ejecuciones(
        numero_parte="NO_EXISTE",
        ruta_db=ruta_db,
    )

    assert len(sin_coincidencias) == 0


def test_consultar_por_usuario(
    ruta_db, datos_ejecucion
):
    guardar_ejecucion(datos_ejecucion, ruta_db)

    registros = consultar_ejecuciones(
        usuario="Pruebas AutoUSMCA",
        ruta_db=ruta_db,
    )

    assert len(registros) == 1


def test_recuperar_ejecucion_inexistente(ruta_db):
    resultado = obtener_ejecucion(
        999, ruta_db
    )

    assert resultado is None


def test_error_no_guarda_datos_incompletos(
    ruta_db, datos_ejecucion
):
    # Provocamos un error eliminando un campo requerido.
    del datos_ejecucion["resultados"][0]["materiales"][0][
        "pais_origen"
    ]

    with pytest.raises(KeyError):
        guardar_ejecucion(
            datos_ejecucion, ruta_db
        )

    # Comprobamos que la transacción fue revertida.
    conexion = sqlite3.connect(ruta_db)

    try:
        total_ejecuciones = conexion.execute(
            "SELECT COUNT(*) FROM ejecuciones"
        ).fetchone()[0]

        total_resultados = conexion.execute(
            "SELECT COUNT(*) FROM resultados"
        ).fetchone()[0]

        total_materiales = conexion.execute(
            "SELECT COUNT(*) FROM detalle_materiales"
        ).fetchone()[0]

    finally:
        conexion.close()

    assert total_ejecuciones == 0
    assert total_resultados == 0
    assert total_materiales == 0
