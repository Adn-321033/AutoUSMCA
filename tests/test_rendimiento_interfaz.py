
import statistics
import time
import tkinter as tk

from src.ui.historial_window import HistorialWindow
from src.ui.config_window import ConfigWindow


def medir_apertura(root, clase_ventana, repeticiones=20):
    """Mide el tiempo de apertura de una ventana Tkinter."""

    tiempos = []

    for _ in range(repeticiones):
        inicio = time.perf_counter()

        ventana = clase_ventana(root)
        ventana.update_idletasks()
        ventana.update()

        duracion = time.perf_counter() - inicio
        tiempos.append(duracion)

        ventana.destroy()
        root.update_idletasks()

    return tiempos


def test_respuesta_pantallas_secundarias():
    """
    RNF-04:
    Medir la apertura de las pantallas de
    historial y configuración.
    """

    root = tk.Tk()
    root.withdraw()

    try:
        resultados = {
            "Historial": medir_apertura(
                root, HistorialWindow
            ),
            "Configuración": medir_apertura(
                root, ConfigWindow
            ),
        }

        for nombre, tiempos in resultados.items():
            ordenados = sorted(tiempos)

            promedio = statistics.mean(tiempos)
            maximo = max(tiempos)

            indice_95 = (
                95 * len(ordenados) + 99
            ) // 100 - 1

            percentil_95 = ordenados[indice_95]

            cumplimiento = sum(
                tiempo < 2.0
                for tiempo in tiempos
            ) / len(tiempos) * 100

            print(
                f"\nPantalla: {nombre}"
                f"\nOperaciones: {len(tiempos)}"
                f"\nTiempo promedio: {promedio:.5f} s"
                f"\nTiempo máximo: {maximo:.5f} s"
                f"\nPercentil 95: {percentil_95:.5f} s"
                f"\nCumplimiento: {cumplimiento:.2f}%"
            )

            assert cumplimiento >= 95.0, (
                f"La pantalla {nombre} no cumple RNF-04."
            )

    finally:
        root.destroy()
