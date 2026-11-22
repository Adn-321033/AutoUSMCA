
import tracemalloc

import pandas as pd

from src.clasificacion import clasificar_materiales
from src.regla_origen import verificar_regla_origen


def test_memoria_500_productos():
    """
    Medición parcial de RNF-06.

    Procesa 500 productos sintéticos con
    40 materiales cada uno.
    """

    cantidad_productos = 500
    materiales_por_producto = 40

    productos = []

    for numero in range(cantidad_productos):
        materiales = pd.DataFrame({
            "ORIGEN": [
                ["MEX", "USA", "CAN", "CHN"][i % 4]
                for i in range(materiales_por_producto)
            ],
            "VALOR US": [
                1.25 + i * 0.05
                for i in range(materiales_por_producto)
            ],
        })

        productos.append(materiales)

    financieros = {
        "labor_day": 15.0,
        "indirect_costs": 3.0,
    }

    tracemalloc.start()

    try:
        resultados = []

        for materiales in productos:
            clasificados = clasificar_materiales(
                materiales
            )

            resultado = verificar_regla_origen(
                clasificados,
                financieros
            )

            resultados.append(resultado)

        memoria_actual, memoria_maxima = (
            tracemalloc.get_traced_memory()
        )

    finally:
        tracemalloc.stop()

    memoria_mb = memoria_maxima / (1024 ** 2)

    print(
        f"\nProductos procesados: {len(resultados)}"
        f"\nMateriales totales: 20000"
        f"\nMemoria máxima rastreada: "
        f"{memoria_mb:.2f} MB"
    )

    assert len(resultados) == 500
    assert memoria_maxima <= 2 * (1024 ** 3)
