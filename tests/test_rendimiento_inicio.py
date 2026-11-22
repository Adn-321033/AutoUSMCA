
import time
import tkinter as tk

from src.ui.main_window import MainWindow


def test_tiempo_inicio_interfaz():
    """
    RNF-16:
    La ventana principal debe inicializarse
    en un máximo de 10 segundos.
    """

    inicio = time.perf_counter()
    root = tk.Tk()

    try:
        root.withdraw()

        MainWindow(root)

        root.update_idletasks()
        root.update()

        tiempo = time.perf_counter() - inicio

        print(
            f"\nTiempo de inicio: {tiempo:.5f} segundos"
        )

        assert tiempo <= 10.0, (
            f"RNF-16 incumplido: {tiempo:.5f} segundos"
        )

    finally:
        root.destroy()
