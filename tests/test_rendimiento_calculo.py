
import time

import pandas as pd

from src.clasificacion import clasificar_materiales
from src.regla_origen import verificar_regla_origen


def test_calculo_500_productos():
    """
    Prueba de rendimiento del núcleo de cálculo.

    Evalúa 500 productos sintéticos con 40
    materiales cada uno: 20,000 materiales.
    """

    cantidad_productos = 500
    materiales_por_producto = 40

    # Generar datos fuera del intervalo medido.
    productos = []

    for numero in range(cantidad_productos):
        materiales = pd.DataFrame({
            "ORIGEN": [
                ["MEX", "USA", "CAN", "CHN"][i % 4]
                for i in range(materiales_por_producto)
            ],
            "VALOR US": [
                1.25 + (i * 0.05)
                for i in range(materiales_por_producto)
            ],
        })

        financieros = {
            "labor_day": 15.0,
            "indirect_costs": 3.0,
        }

        productos.append(
            (materiales, financieros)
        )

    inicio = time.perf_counter()

    resultados = []

    for materiales, financieros in productos:
        clasificados = clasificar_materiales(
            materiales
        )

        resultado = verificar_regla_origen(
            clasificados,
            financieros
        )

        resultados.append(resultado)

    tiempo = time.perf_counter() - inicio

    print(
        f"\nProductos procesados: {len(resultados)}"
        f"\nMateriales totales: "
        f"{cantidad_productos * materiales_por_producto}"
        f"\nTiempo de cálculo: {tiempo:.5f} segundos"
        f"\nReferencia RNF-01: 60 segundos"
    )

    assert len(resultados) == 500

    assert all(
        resultado["costo_neto"] > 0
        for resultado in resultados
    )

    assert tiempo <= 60.0, (
        f"Tiempo superior a 60 segundos: {tiempo:.5f}"
    )
