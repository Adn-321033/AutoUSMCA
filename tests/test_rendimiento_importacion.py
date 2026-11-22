
import time
import pandas as pd
import pytest

from src.services.import_service import ImportService


@pytest.mark.parametrize("formato", ["xlsx", "csv"])
def test_importacion_5000_registros(tmp_path, formato):
    """
    RNF-02:
    Importar 5000 registros en un máximo de 15 segundos.

    Utiliza datos sintéticos para no exponer
    información empresarial.
    """

    cantidad = 5000

    # Generar registros de prueba.
    datos = pd.DataFrame({
        "PARTE": [
            f"MAT{i:06d}"
            for i in range(cantidad)
        ],
        "DESCRIPCION INGLES": [
            f"Material de prueba {i}"
            for i in range(cantidad)
        ],
        "ORIGEN": [
            ["MEX", "USA", "CAN", "CHN"][i % 4]
            for i in range(cantidad)
        ],
        "VALOR US": [
            10.25 + i * 0.01
            for i in range(cantidad)
        ],
        "FRACCION MX": ["39269099"] * cantidad,
    })

    ruta = tmp_path / f"reporte_5000.{formato}"

    if formato == "xlsx":
        datos.to_excel(ruta, index=False)
    else:
        datos.to_csv(ruta, index=False)

    # Medir solamente el tiempo de importación.
    inicio = time.perf_counter()

    resultado = ImportService.cargar_reporte_aduanas(
        ruta
    )

    tiempo = time.perf_counter() - inicio

    print(
        f"\nFormato: {formato.upper()}"
        f"\nRegistros: {len(resultado)}"
        f"\nTiempo de importación: {tiempo:.5f} segundos"
        f"\nLímite RNF-02: 15 segundos"
    )

    assert len(resultado) == cantidad
    assert tiempo <= 15.0, (
        f"RNF-02 incumplido: {tiempo:.5f} segundos"
    )
