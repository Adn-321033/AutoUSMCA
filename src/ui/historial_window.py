
import tkinter as tk
from tkinter import ttk, messagebox

from src.repositories.historial_repository import (
    consultar_ejecuciones,
    obtener_ejecucion,
)


class HistorialWindow(tk.Toplevel):
    """Ventana de consulta del historial de AutoUSMCA."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("AutoUSMCA - Historial de ejecuciones")
        self.geometry("1000x600")
        self.minsize(800, 450)

        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.usuario = tk.StringVar()
        self.numero_parte = tk.StringVar()
        self.fecha_desde = tk.StringVar()
        self.fecha_hasta = tk.StringVar()

        self.crear_interfaz()
        self.cargar_historial()

    def crear_interfaz(self):
        titulo = ttk.Label(
            self,
            text="Historial de ejecuciones",
            font=("Arial", 17, "bold"),
        )
        titulo.pack(pady=(15, 10))

        filtros = ttk.LabelFrame(
            self,
            text="Filtros de búsqueda",
            padding=12,
        )
        filtros.pack(fill="x", padx=20, pady=10)

        campos = [
            ("Usuario:", self.usuario),
            ("Número de parte:", self.numero_parte),
            ("Desde (AAAA-MM-DD):", self.fecha_desde),
            ("Hasta (AAAA-MM-DD):", self.fecha_hasta),
        ]

        for indice, (etiqueta, variable) in enumerate(campos):
            ttk.Label(
                filtros,
                text=etiqueta,
            ).grid(
                row=indice // 2,
                column=(indice % 2) * 2,
                sticky="w",
                padx=5,
                pady=5,
            )

            ttk.Entry(
                filtros,
                textvariable=variable,
                width=23,
            ).grid(
                row=indice // 2,
                column=(indice % 2) * 2 + 1,
                padx=5,
                pady=5,
            )

        botones = ttk.Frame(self)
        botones.pack(fill="x", padx=20, pady=5)

        ttk.Button(
            botones,
            text="Buscar",
            command=self.cargar_historial,
        ).pack(side="left", padx=5)

        ttk.Button(
            botones,
            text="Limpiar filtros",
            command=self.limpiar_filtros,
        ).pack(side="left", padx=5)

        ttk.Button(
            botones,
            text="Ver detalle",
            command=self.ver_detalle,
        ).pack(side="right", padx=5)

        # Tabla del historial
        contenedor = ttk.Frame(self)
        contenedor.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10,
        )

        columnas = (
            "id",
            "fecha",
            "usuario",
            "total",
            "cumplen",
            "no_cumplen",
            "estado",
        )

        self.tabla = ttk.Treeview(
            contenedor,
            columns=columnas,
            show="headings",
            selectmode="browse",
        )

        encabezados = {
            "id": "ID",
            "fecha": "Fecha",
            "usuario": "Usuario",
            "total": "Productos",
            "cumplen": "Pasan",
            "no_cumplen": "No pasan",
            "estado": "Estado",
        }

        for columna, encabezado in encabezados.items():
            self.tabla.heading(
                columna,
                text=encabezado,
            )

            self.tabla.column(
                columna,
                width=125 if columna != "id" else 55,
                anchor="center",
            )

        desplazamiento = ttk.Scrollbar(
            contenedor,
            orient="vertical",
            command=self.tabla.yview,
        )

        self.tabla.configure(
            yscrollcommand=desplazamiento.set
        )

        self.tabla.pack(
            side="left",
            fill="both",
            expand=True,
        )

        desplazamiento.pack(
            side="right",
            fill="y",
        )

        self.tabla.bind(
            "<Double-1>",
            lambda evento: self.ver_detalle(),
        )

        self.estado = tk.StringVar(
            value="Sin consultas realizadas."
        )

        ttk.Label(
            self,
            textvariable=self.estado,
        ).pack(pady=(0, 10))

    def cargar_historial(self):
        try:
            registros = consultar_ejecuciones(
                fecha_desde=self.fecha_desde.get().strip() or None,
                fecha_hasta=self.fecha_hasta.get().strip() or None,
                usuario=self.usuario.get().strip() or None,
                numero_parte=self.numero_parte.get().strip() or None,
            )

            for elemento in self.tabla.get_children():
                self.tabla.delete(elemento)

            for registro in registros:
                self.tabla.insert(
                    "",
                    "end",
                    iid=str(registro["id"]),
                    values=(
                        registro["id"],
                        registro["fecha_ejecucion"],
                        registro["usuario"] or "",
                        registro["total_partes"],
                        registro["partes_cumplen"],
                        registro["partes_no_cumplen"],
                        registro["estado"],
                    ),
                )

            self.estado.set(
                f"Ejecuciones encontradas: {len(registros)}"
            )

        except Exception as error:
            messagebox.showerror(
                "Error de consulta",
                str(error),
                parent=self,
            )

    def limpiar_filtros(self):
        self.usuario.set("")
        self.numero_parte.set("")
        self.fecha_desde.set("")
        self.fecha_hasta.set("")
        self.cargar_historial()

    def ver_detalle(self):
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning(
                "Seleccione una ejecución",
                "Debe seleccionar un registro del historial.",
                parent=self,
            )
            return

        ejecucion_id = int(seleccion[0])

        try:
            ejecucion = obtener_ejecucion(ejecucion_id)

            if ejecucion is None:
                raise ValueError(
                    "La ejecución seleccionada no existe."
                )

            self.mostrar_detalle(ejecucion)

        except Exception as error:
            messagebox.showerror(
                "Error",
                str(error),
                parent=self,
            )

    def mostrar_detalle(self, ejecucion):
        ventana = tk.Toplevel(self)
        ventana.title(
            f"Detalle de ejecución {ejecucion['id']}"
        )
        ventana.geometry("760x510")
        ventana.transient(self)

        texto = tk.Text(
            ventana,
            wrap="word",
            padx=15,
            pady=15,
        )
        texto.pack(fill="both", expand=True)

        texto.insert(
            "end",
            f"EJECUCIÓN: {ejecucion['id']}\n"
            f"Fecha: {ejecucion['fecha_ejecucion']}\n"
            f"Usuario: {ejecucion['usuario']}\n"
            f"Estado: {ejecucion['estado']}\n\n"
        )

        for resultado in ejecucion["resultados"]:
            porcentaje = resultado["porcentaje_no_regional"]
            cumplimiento = (
                "PASA" if resultado["cumple"] else "NO PASA"
            )

            texto.insert(
                "end",
                f"{'=' * 45}\n"
                f"Producto: {resultado['numero_parte']}\n"
                f"Costo neto: {resultado['costo_neto']:.5f}\n"
                f"Costo no originario: "
                f"{resultado['costo_no_originario']:.5f}\n"
                f"Contenido no regional: {porcentaje:.5f}%\n"
                f"Resultado: {cumplimiento}\n"
                f"Materiales: {len(resultado['materiales'])}\n"
                f"Excel: {resultado['archivo_excel']}\n"
                f"PDF: {resultado['archivo_pdf']}\n\n"
            )

            for material in resultado["materiales"]:
                texto.insert(
                    "end",
                    f"  {material['numero_parte']} | "
                    f"{material['pais_origen']} | "
                    f"Peso: {material['kilogramos']:.5f} | "
                    f"Costo: {material['costo_total']:.5f}\n"
                )

            texto.insert("end", "\n")

        texto.configure(state="disabled")
