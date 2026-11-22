
import os
import time
import threading

import pandas as pd
import psutil

from src.clasificacion import clasificar_materiales
from src.regla_origen import verificar_regla_origen


def test_memoria_real_500_productos():
    """
    Medición de memoria residente (RSS).

    Escenario:
    - 500 productos
    - 40 materiales por producto
    - 20,000 materiales en total

    Mide el consumo del proceso durante
    la preparación y ejecución del cálculo.
    """

    proceso = psutil.Process(os.getpid())

    memoria_inicial = proceso.memory_info().rss
    muestras = [memoria_inicial]

    detener = threading.Event()

    def monitorear_memoria():
        while not detener.is_set():
            muestras.append(
                proceso.memory_info().rss
            )
            time.sleep(0.01)

    monitor = threading.Thread(
        target=monitorear_memoria,
        daemon=True,
    )

    monitor.start()

    try:
        productos = []

        for numero in range(500):
            materiales = pd.DataFrame({
                "ORIGEN": [
                    ["MEX", "USA", "CAN", "CHN"][i % 4]
                    for i in range(40)
                ],
                "VALOR US": [
                    1.25 + i * 0.05
                    for i in range(40)
                ],
            })

            productos.append(materiales)

        financieros = {
            "labor_day": 15.0,
            "indirect_costs": 3.0,
        }

        resultados = []

        for materiales in productos:
            clasificados = clasificar_materiales(
                materiales
            )

            resultado = verificar_regla_origen(
                clasificados,
                financieros,
            )

            resultados.append(resultado)

        muestras.append(
            proceso.memory_info().rss
        )

    finally:
        detener.set()
        monitor.join()
        muestras.append(
            proceso.memory_info().rss
        )

    memoria_maxima = max(muestras)
    memoria_mb = memoria_maxima / (1024 ** 2)
    incremento_mb = (
        memoria_maxima - memoria_inicial
    ) / (1024 ** 2)

    print(
        f"\nProductos procesados: {len(resultados)}"
        f"\nMateriales totales: 20000"
        f"\nMemoria RSS máxima: {memoria_mb:.2f} MB"
        f"\nIncremento respecto al inicio: "
        f"{incremento_mb:.2f} MB"
        f"\nLímite RNF-06: 2048 MB"
    )

    assert len(resultados) == 500
    assert memoria_maxima <= 2 * (1024 ** 3), (
        "RNF-06: memoria superior a 2 GB."
    )
