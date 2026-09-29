import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoUSMCA")
        self.root.geometry("850x550")
        self.root.minsize(750, 500)

        self.archivo_costos = None
        self.archivo_consumos = None

        self.crear_interfaz()

    def crear_interfaz(self):
        titulo = tk.Label(
            self.root,
            text="AutoUSMCA",
            font=("Arial", 22, "bold")
        )
        titulo.pack(pady=(20, 5))

        subtitulo = tk.Label(
            self.root,
            text="Sistema de Automatización para el Cálculo de Contenido Regional",
            font=("Arial", 11)
        )
        subtitulo.pack(pady=(0, 20))

        frame_archivos = tk.LabelFrame(
            self.root,
            text="Archivos de entrada",
            padx=15,
            pady=15
        )
        frame_archivos.pack(fill="x", padx=30, pady=10)

        tk.Label(
            frame_archivos,
            text="Reporte de costos:"
        ).grid(row=0, column=0, sticky="w", pady=8)

        self.lbl_costos = tk.Label(
            frame_archivos,
            text="Ningún archivo seleccionado",
            anchor="w"
        )
        self.lbl_costos.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=10
        )

        btn_costos = tk.Button(
            frame_archivos,
            text="Seleccionar",
            command=self.seleccionar_costos
        )
        btn_costos.grid(row=0, column=2)

        tk.Label(
            frame_archivos,
            text="Reporte de consumos:"
        ).grid(row=1, column=0, sticky="w", pady=8)

        self.lbl_consumos = tk.Label(
            frame_archivos,
            text="Ningún archivo seleccionado",
            anchor="w"
        )
        self.lbl_consumos.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=10
        )

        btn_consumos = tk.Button(
            frame_archivos,
            text="Seleccionar",
            command=self.seleccionar_consumos
        )
        btn_consumos.grid(row=1, column=2)

        frame_archivos.columnconfigure(1, weight=1)

        self.btn_procesar = tk.Button(
            self.root,
            text="Procesar archivos",
            width=20,
            height=2,
            command=self.procesar
        )
        self.btn_procesar.pack(pady=15)

        frame_resultados = tk.LabelFrame(
            self.root,
            text="Resultados",
            padx=15,
            pady=15
        )
        frame_resultados.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(5, 20)
        )

        self.lbl_estado = tk.Label(
            frame_resultados,
            text="Esperando archivos para iniciar el procesamiento.",
            anchor="w"
        )
        self.lbl_estado.pack(fill="x")

    def seleccionar_costos(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar reporte de costos",
            filetypes=[
                ("Archivos Excel", "*.xlsx"),
                ("Archivos CSV", "*.csv"),
                ("Todos los archivos", "*.*")
            ]
        )

        if archivo:
            self.archivo_costos = archivo
            self.lbl_costos.config(text=Path(archivo).name)

    def seleccionar_consumos(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar reporte de consumos",
            filetypes=[
                ("Archivos Excel", "*.xlsx"),
                ("Archivos CSV", "*.csv"),
                ("Todos los archivos", "*.*")
            ]
        )

        if archivo:
            self.archivo_consumos = archivo
            self.lbl_consumos.config(text=Path(archivo).name)

    def procesar(self):
        if not self.archivo_costos or not self.archivo_consumos:
            messagebox.showwarning(
                "Archivos incompletos",
                "Debe seleccionar el reporte de costos y el reporte de consumos."
            )
            return

        self.lbl_estado.config(
            text="Archivos seleccionados correctamente. "
                 "El módulo de procesamiento será implementado posteriormente."
        )


def iniciar_aplicacion():
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()