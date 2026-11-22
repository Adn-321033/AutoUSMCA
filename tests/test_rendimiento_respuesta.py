
import time
import statistics

from src.configuracion import cargar_configuracion


def test_tiempo_respuesta_configuracion():
    """
    Medición complementaria para RNF-04.

    Realiza 100 consultas de configuración
    y verifica que al menos el 95% se
    complete en menos de 2 segundos.
    """

    tiempos = []

    for _ in range(100):
        inicio = time.perf_counter()

        configuracion = cargar_configuracion()

        duracion = time.perf_counter() - inicio

        assert configuracion is not None

        tiempos.append(duracion)

    tiempos_ordenados = sorted(tiempos)

    indice_95 = 94
    percentil_95 = tiempos_ordenados[indice_95]

    promedio = statistics.mean(tiempos)
    maximo = max(tiempos)

    operaciones_cumplen = sum(
        tiempo < 2.0
        for tiempo in tiempos
    )

    porcentaje_cumplimiento = (
        operaciones_cumplen / len(tiempos)
    ) * 100

    print(
        f"\nOperaciones evaluadas: {len(tiempos)}"
        f"\nTiempo promedio: {promedio:.6f} segundos"
        f"\nTiempo máximo: {maximo:.6f} segundos"
        f"\nPercentil 95: {percentil_95:.6f} segundos"
        f"\nOperaciones menores a 2 s: "
        f"{operaciones_cumplen}"
        f"\nCumplimiento: "
        f"{porcentaje_cumplimiento:.2f}%"
    )

    assert porcentaje_cumplimiento >= 95.0
