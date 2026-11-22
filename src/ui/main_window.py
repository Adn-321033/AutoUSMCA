"""Ventana principal de AutoUSMCA."""

import os
import tkinter as tk
from pathlib import Path
from queue import Empty, Queue
from threading import Thread
from tkinter import filedialog, messagebox, ttk

from src.procesamiento_usmca import procesar_producto, procesar_todos_productos
from src.ui.config_window import ConfigWindow
from src.ui.historial_window import HistorialWindow
from src.rutas import BASE_DIR


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoUSMCA")
        self.root.geometry("950x650")
        self.root.minsize(650, 420)

        self.archivo_costos = None
        self.archivo_consumos = None
        self.reporte_excel = None
        self.reporte_pdf = None
        self.numero_parte = tk.StringVar(master=root)
        self.estado = tk.StringVar(
            master=root,
            value="Seleccione los archivos para comenzar.",
        )

        self.procesando = False
        self.cola_trabajo = Queue()
        self.crear_interfaz()

        # Todas las actualizaciones de Tkinter se ejecutan en el hilo principal.
        self.root.after(100, self._revisar_cola_trabajo)

    def crear_interfaz(self):
        # Contenedor desplazable de la ventana principal.
        contenedor_principal = ttk.Frame(self.root)
        contenedor_principal.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            contenedor_principal,
            borderwidth=0,
            highlightthickness=0,
        )
        self.scroll_vertical = ttk.Scrollbar(
            contenedor_principal,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.canvas.configure(yscrollcommand=self.scroll_vertical.set)
        self.scroll_vertical.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.contenido = ttk.Frame(self.canvas)
        self.ventana_contenido = self.canvas.create_window(
            (0, 0), window=self.contenido, anchor="nw"
        )
        self.contenido.bind("<Configure>", self._actualizar_scroll)
        self.canvas.bind("<Configure>", self._ajustar_ancho_contenido)
        self.root.bind_all("<MouseWheel>", self._scroll_mouse, add="+")

        ttk.Label(
            self.contenido,
            text="AutoUSMCA",
            font=("Arial", 22, "bold"),
        ).pack(pady=(20, 5))

        ttk.Label(
            self.contenido,
            text="Sistema de Automatización para el Cálculo de Contenido Regional",
            font=("Arial", 11),
        ).pack(pady=(0, 15))

        # Archivos de entrada.
        frame_archivos = ttk.LabelFrame(
            self.contenido, text="Archivos de entrada", padding=15
        )
        frame_archivos.pack(fill="x", padx=25, pady=10)
        frame_archivos.columnconfigure(1, weight=1)

        ttk.Label(
            frame_archivos, text="Reporte de costos de Finanzas:"
        ).grid(row=0, column=0, sticky="w", pady=8)
        self.lbl_costos = ttk.Label(
            frame_archivos, text="Ningún archivo seleccionado", anchor="w"
        )
        self.lbl_costos.grid(row=0, column=1, sticky="ew", padx=10)
        ttk.Button(
            frame_archivos, text="Seleccionar", command=self.seleccionar_costos
        ).grid(row=0, column=2)

        ttk.Label(
            frame_archivos, text="Reporte de materiales de Aduanas:"
        ).grid(row=1, column=0, sticky="w", pady=8)
        self.lbl_consumos = ttk.Label(
            frame_archivos, text="Ningún archivo seleccionado", anchor="w"
        )
        self.lbl_consumos.grid(row=1, column=1, sticky="ew", padx=10)
        ttk.Button(
            frame_archivos, text="Seleccionar", command=self.seleccionar_consumos
        ).grid(row=1, column=2)

        # Procesamiento individual.
        frame_producto = ttk.LabelFrame(
            self.contenido, text="Producto terminado", padding=12
        )
        frame_producto.pack(fill="x", padx=25, pady=10)
        ttk.Label(frame_producto, text="Número de parte:").pack(
            side="left", padx=(0, 10)
        )
        self.entrada_parte = ttk.Entry(
            frame_producto, textvariable=self.numero_parte, width=25
        )
        self.entrada_parte.pack(side="left")

        frame_acciones = ttk.Frame(self.contenido)
        frame_acciones.pack(pady=8)
        self.btn_procesar = ttk.Button(
            frame_acciones, text="Procesar producto", command=self.procesar
        )
        self.btn_procesar.pack(side="left", padx=5)
        self.btn_procesar_todos = ttk.Button(
            frame_acciones,
            text="Procesar todos los productos",
            command=self.procesar_todos,
        )
        self.btn_procesar_todos.pack(side="left", padx=5)

        frame_opciones = ttk.Frame(self.contenido)
        frame_opciones.pack(pady=(0, 10))
        self.btn_historial = ttk.Button(
            frame_opciones, text="Consultar historial", command=self.abrir_historial
        )
        self.btn_historial.pack(side="left", padx=5)
        self.btn_configuracion = ttk.Button(
            frame_opciones, text="Configuración", command=self.abrir_configuracion
        )
        self.btn_configuracion.pack(side="left", padx=5)

        self.barra_progreso = ttk.Progressbar(
            self.contenido, mode="indeterminate", length=350
        )
        self.barra_progreso.pack(fill="x", padx=40, pady=8)

        # Resultados. La altura del contenido hace que el Canvas pueda desplazarse.
        frame_resultados = ttk.LabelFrame(
            self.contenido, text="Resultados del procesamiento", padding=15
        )
        frame_resultados.pack(fill="x", padx=25, pady=(10, 20))

        self.lbl_estado = ttk.Label(
            frame_resultados,
            textvariable=self.estado,
            justify="left",
            anchor="nw",
        )
        self.lbl_estado.pack(fill="x", anchor="w")

        # Botones en dos filas para no ocultarse horizontalmente.
        frame_reportes = ttk.Frame(frame_resultados)
        frame_reportes.pack(fill="x", pady=(12, 0))
        self.btn_excel = ttk.Button(
            frame_reportes,
            text="Abrir reporte Excel",
            command=self.abrir_reporte_excel,
            state="disabled",
        )
        self.btn_excel.grid(row=0, column=0, padx=(0, 10), pady=4, sticky="w")
        self.btn_pdf = ttk.Button(
            frame_reportes,
            text="Abrir reporte PDF",
            command=self.abrir_reporte_pdf,
            state="disabled",
        )
        self.btn_pdf.grid(row=0, column=1, pady=4, sticky="w")
        self.btn_carpeta = ttk.Button(
            frame_reportes,
            text="Abrir carpeta de reportes",
            command=self.abrir_carpeta_reportes,
            state="disabled",
        )
        self.btn_carpeta.grid(row=1, column=0, columnspan=2, pady=4, sticky="w")

    def _actualizar_scroll(self, evento=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _ajustar_ancho_contenido(self, evento):
        self.canvas.itemconfigure(self.ventana_contenido, width=evento.width)
        if hasattr(self, "lbl_estado"):
            self.lbl_estado.configure(wraplength=max(250, evento.width - 110))

    def _scroll_mouse(self, evento):
        try:
            widget = self.root.winfo_containing(
                self.root.winfo_pointerx(), self.root.winfo_pointery()
            )
            if widget is None or widget.winfo_toplevel() != self.root:
                return
            region = self.canvas.bbox("all")
            if region is None or region[3] - region[1] <= self.canvas.winfo_height():
                return
            if evento.delta:
                direccion = -1 if evento.delta > 0 else 1
                self.canvas.yview_scroll(direccion * 3, "units")
        except tk.TclError:
            pass

    def abrir_historial(self):
        HistorialWindow(self.root)

    def abrir_configuracion(self):
        ConfigWindow(self.root)

    def seleccionar_costos(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar reporte de Finanzas",
            filetypes=[("Archivos Excel", "*.xlsx"), ("Archivos CSV", "*.csv")],
        )
        if archivo:
            self.archivo_costos = Path(archivo)
            self.lbl_costos.configure(text=self.archivo_costos.name)

    def seleccionar_consumos(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar reporte de Aduanas",
            filetypes=[("Archivos Excel", "*.xlsx"), ("Archivos CSV", "*.csv")],
        )
        if archivo:
            self.archivo_consumos = Path(archivo)
            self.lbl_consumos.configure(text=self.archivo_consumos.name)

    def _validar_archivos(self):
        if not self.archivo_costos or not self.archivo_consumos:
            messagebox.showwarning(
                "Archivos incompletos",
                "Seleccione los reportes de Aduanas y Finanzas.",
                parent=self.root,
            )
            return None
        plantilla = BASE_DIR / "data" / "input" / "P_WORKSHEET.xlsx"
        if not plantilla.is_file():
            messagebox.showerror(
                "Plantilla no encontrada",
                "No se encontró la plantilla de resultados en Excel.",
                parent=self.root,
            )
            return None
        return plantilla

    def _iniciar_procesamiento(self, masivo=False):
        self.procesando = True
        self.btn_procesar.configure(state="disabled")
        self.btn_procesar_todos.configure(state="disabled")
        self.btn_excel.configure(state="disabled")
        self.btn_pdf.configure(state="disabled")
        self.btn_carpeta.configure(state="disabled")
        self.reporte_excel = None
        self.reporte_pdf = None
        self.barra_progreso.stop()
        self.barra_progreso.configure(
            mode="determinate" if masivo else "indeterminate",
            maximum=100,
            value=0,
        )
        if not masivo:
            self.barra_progreso.start(10)

    def procesar(self):
        if self.procesando:
            return
        plantilla = self._validar_archivos()
        if plantilla is None:
            return
        parte = self.numero_parte.get().strip().upper()
        if not parte:
            messagebox.showwarning(
                "Número de parte",
                "Escriba el número de parte que desea procesar.",
                parent=self.root,
            )
            self.entrada_parte.focus_set()
            return

        self._iniciar_procesamiento(masivo=False)
        self.estado.set(f"Procesando el producto {parte}...\nValidando archivos y calculando resultados.")
        Thread(
            target=self._ejecutar_procesamiento,
            args=(parte, self.archivo_consumos, self.archivo_costos, plantilla),
            daemon=True,
        ).start()

    def procesar_todos(self):
        if self.procesando:
            return
        plantilla = self._validar_archivos()
        if plantilla is None:
            return
        confirmar = messagebox.askyesno(
            "Procesamiento masivo",
            "¿Desea procesar todos los productos únicos del reporte de Aduanas?\n\n"
            "Se generará un Excel y un PDF por producto procesado correctamente.\n\n"
            "Los reportes anteriores del mismo producto podrían reemplazarse.",
            parent=self.root,
        )
        if not confirmar:
            return

        self._iniciar_procesamiento(masivo=True)
        self.estado.set("Iniciando procesamiento masivo...\nImportando y validando los reportes.")
        Thread(
            target=self._ejecutar_lote,
            args=(self.archivo_consumos, self.archivo_costos, plantilla),
            daemon=True,
        ).start()

    def _ejecutar_procesamiento(self, parte, consumos, costos, plantilla):
        try:
            resultado = procesar_producto(
                parte,
                BASE_DIR,
                archivo_aduanas=consumos,
                archivo_finanzas=costos,
                plantilla_excel=plantilla,
            )
            self.cola_trabajo.put(("individual_completado", resultado))
        except Exception as error:
            self.cola_trabajo.put(("error", str(error)))

    def _ejecutar_lote(self, consumos, costos, plantilla):
        def informar_progreso(actual, total, parte):
            self.cola_trabajo.put(("progreso", actual, total, parte))

        try:
            resultado = procesar_todos_productos(
                directorio_base=BASE_DIR,
                archivo_aduanas=consumos,
                archivo_finanzas=costos,
                plantilla_excel=plantilla,
                progreso=informar_progreso,
            )
            self.cola_trabajo.put(("lote_completado", resultado))
        except Exception as error:
            self.cola_trabajo.put(("error", str(error)))

    def _revisar_cola_trabajo(self):
        try:
            while True:
                try:
                    mensaje = self.cola_trabajo.get_nowait()
                except Empty:
                    break

                tipo = mensaje[0]
                if tipo == "progreso":
                    _, actual, total, parte = mensaje
                    porcentaje = actual / total * 100 if total else 0
                    self.barra_progreso.configure(value=porcentaje)
                    self.estado.set(
                        "Procesamiento masivo en ejecución.\n"
                        f"Producto: {parte}\n"
                        f"Avance: {actual} de {total}\n"
                        f"Progreso: {porcentaje:.1f}%"
                    )
                elif tipo == "individual_completado":
                    self._mostrar_resultados(mensaje[1])
                elif tipo == "lote_completado":
                    self._mostrar_resultados_lote(mensaje[1])
                elif tipo == "error":
                    self._mostrar_error(mensaje[1])
        finally:
            try:
                if self.root.winfo_exists():
                    self.root.after(100, self._revisar_cola_trabajo)
            except tk.TclError:
                pass

    def _finalizar_procesamiento(self):
        self.procesando = False
        self.barra_progreso.stop()
        self.btn_procesar.configure(state="normal")
        self.btn_procesar_todos.configure(state="normal")

    def _mostrar_resultados(self, datos):
        self._finalizar_procesamiento()
        self.reporte_excel = Path(datos["archivo"])
        self.reporte_pdf = Path(datos["archivo_pdf"])
        self.btn_excel.configure(state="normal")
        self.btn_pdf.configure(state="normal")
        self.btn_carpeta.configure(state="normal")

        calculo = datos["resultado"]
        cumplimiento = "PASA" if calculo["cumple"] else "NO PASA"
        self.estado.set(
            f"Producto: {datos['producto']}\n"
            f"Materiales originales: {datos['materiales_originales']}\n"
            f"Materiales consolidados: {datos['materiales_consolidados']}\n\n"
            f"Total materiales: {calculo['total_materiales']:.5f}\n"
            f"Labor Day: {calculo['labor_day']:.5f}\n"
            f"Indirect Costs: {calculo['indirect_costs']:.5f}\n"
            f"Costo neto: {calculo['costo_neto']:.5f}\n"
            f"Costo no originario: {calculo['costo_no_originario']:.5f}\n\n"
            f"Contenido no regional: {calculo['porcentaje']:.5f}%\n"
            f"Umbral aplicado: {calculo['umbral_utilizado']:.2f}%\n"
            f"Resultado: {cumplimiento}\n\n"
            f"Historial ID: {datos['ejecucion_id']}\n"
            f"Excel: {datos['archivo']}\n"
            f"PDF: {datos['archivo_pdf']}"
        )
        messagebox.showinfo(
            "Procesamiento completado",
            f"El producto {datos['producto']} se procesó correctamente.",
            parent=self.root,
        )

    def _mostrar_resultados_lote(self, datos):
        self._finalizar_procesamiento()
        errores = datos["errores"]
        resumen = (
            "PROCESAMIENTO MASIVO FINALIZADO\n\n"
            f"Productos únicos encontrados: {datos['total_productos']}\n"
            f"Apariciones adicionales agrupadas: {datos['apariciones_duplicadas']}\n"
            f"Productos procesados: {datos['procesados']}\n"
            f"Productos que cumplen: {datos['cumplen']}\n"
            f"Productos que no cumplen: {datos['no_cumplen']}\n"
            f"Productos con errores: {len(errores)}\n\n"
            f"ID del historial: {datos['ejecucion_id']}\n"
            f"Carpeta de reportes: {datos['directorio_salida']}"
        )
        if errores:
            resumen += "\n\nPrimeros errores detectados:"
            for error in errores[:10]:
                resumen += f"\n- {error['producto']}: {error['error']}"
            if len(errores) > 10:
                resumen += "\nConsulte la bitácora para revisar los demás errores."
        self.estado.set(resumen)
        self.btn_carpeta.configure(state="normal")
        messagebox.showinfo(
            "Procesamiento masivo terminado",
            f"Se procesaron correctamente {datos['procesados']} "
            f"de {datos['total_productos']} productos.\n\n"
            f"Productos con errores: {len(errores)}",
            parent=self.root,
        )

    def _mostrar_error(self, mensaje):
        self._finalizar_procesamiento()
        self.estado.set(
            "No fue posible completar el procesamiento.\n"
            f"Detalle: {mensaje}"
        )
        messagebox.showerror("Error de procesamiento", mensaje, parent=self.root)

    def abrir_archivo_generado(self, ruta_archivo):
        if ruta_archivo is None:
            messagebox.showwarning(
                "Reporte no disponible",
                "Todavía no se ha generado este reporte.",
                parent=self.root,
            )
            return
        ruta = Path(ruta_archivo)
        if not ruta.is_file():
            messagebox.showerror(
                "Archivo no encontrado",
                "El reporte ya no existe en la ubicación registrada.",
                parent=self.root,
            )
            return
        try:
            os.startfile(str(ruta.resolve()))
        except OSError as error:
            messagebox.showerror("Error al abrir el reporte", str(error), parent=self.root)

    def abrir_reporte_excel(self):
        self.abrir_archivo_generado(self.reporte_excel)

    def abrir_reporte_pdf(self):
        self.abrir_archivo_generado(self.reporte_pdf)

    def abrir_carpeta_reportes(self):
        carpeta = BASE_DIR / "data" / "output"
        if not carpeta.is_dir():
            messagebox.showerror(
                "Carpeta no encontrada",
                "No se encontró la carpeta de reportes.",
                parent=self.root,
            )
            return
        try:
            os.startfile(str(carpeta.resolve()))
        except OSError as error:
            messagebox.showerror("Error al abrir carpeta", str(error), parent=self.root)


def iniciar_aplicacion():
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()
