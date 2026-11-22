
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from src.configuracion import (
    cargar_configuracion,
    guardar_configuracion,
    normalizar_texto,
    validar_configuracion,
    PAISES_REGIONALES,
)


class ConfigWindow(tk.Toplevel):
    """Administración de parámetros de AutoUSMCA."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("AutoUSMCA - Configuración")
        self.geometry("750x620")
        self.minsize(650, 500)
        self.transient(parent)

        try:
            self.configuracion = cargar_configuracion()
        except ValueError as error:
            messagebox.showerror(
                "Error de configuración",
                str(error),
                parent=self,
            )
            self.destroy()
            return

        self.umbral = tk.StringVar(
            value=str(
                self.configuracion["umbral_porcentaje"]
            )
        )

        self.crear_interfaz()
        self.actualizar_catalogo()

    def crear_interfaz(self):
        ttk.Label(
            self,
            text="Configuración de AutoUSMCA",
            font=("Arial", 17, "bold"),
        ).pack(pady=(15, 10))

        # Configuración del umbral
        marco_umbral = ttk.LabelFrame(
            self,
            text="Umbral de cumplimiento",
            padding=15,
        )
        marco_umbral.pack(
            fill="x", padx=20, pady=10
        )

        ttk.Label(
            marco_umbral,
            text="Porcentaje máximo permitido:",
        ).pack(side="left", padx=5)

        ttk.Entry(
            marco_umbral,
            textvariable=self.umbral,
            width=12,
        ).pack(side="left", padx=5)

        ttk.Label(
            marco_umbral,
            text="%",
        ).pack(side="left")

        # Catálogo de equivalencias
        marco_catalogo = ttk.LabelFrame(
            self,
            text="Catálogo de equivalencias de países",
            padding=12,
        )
        marco_catalogo.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10,
        )

        columnas = ("nombre", "codigo")

        self.tabla = ttk.Treeview(
            marco_catalogo,
            columns=columnas,
            show="headings",
            selectmode="browse",
        )

        self.tabla.heading(
            "nombre", text="Nombre o equivalencia"
        )
        self.tabla.heading(
            "codigo", text="Código normalizado"
        )

        self.tabla.column(
            "nombre", width=350
        )
        self.tabla.column(
            "codigo", width=180, anchor="center"
        )

        self.tabla.pack(
            fill="both", expand=True
        )

        botones_catalogo = ttk.Frame(self)
        botones_catalogo.pack(pady=5)

        ttk.Button(
            botones_catalogo,
            text="Agregar equivalencia",
            command=self.agregar_equivalencia,
        ).pack(side="left", padx=5)

        ttk.Button(
            botones_catalogo,
            text="Modificar",
            command=self.modificar_equivalencia,
        ).pack(side="left", padx=5)

        ttk.Button(
            botones_catalogo,
            text="Eliminar",
            command=self.eliminar_equivalencia,
        ).pack(side="left", padx=5)

        # Guardar y cancelar
        botones_finales = ttk.Frame(self)
        botones_finales.pack(pady=15)

        ttk.Button(
            botones_finales,
            text="Guardar cambios",
            command=self.guardar,
        ).pack(side="left", padx=10)

        ttk.Button(
            botones_finales,
            text="Cerrar",
            command=self.destroy,
        ).pack(side="left", padx=10)

        ttk.Label(
            self,
            text=(
                "Los cambios se aplicarán a los "
                "procesamientos posteriores."
            ),
        ).pack(pady=(0, 10))

    def actualizar_catalogo(self):
        for elemento in self.tabla.get_children():
            self.tabla.delete(elemento)

        equivalencias = self.configuracion[
            "equivalencias_paises"
        ]

        for nombre, codigo in sorted(
            equivalencias.items()
        ):
            self.tabla.insert(
                "",
                "end",
                iid=nombre,
                values=(nombre, codigo),
            )

    def obtener_seleccion(self):
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning(
                "Selección requerida",
                "Seleccione una equivalencia.",
                parent=self,
            )
            return None

        return seleccion[0]

    def agregar_equivalencia(self):
        nombre = simpledialog.askstring(
            "Nueva equivalencia",
            "Nombre o variante del país:",
            parent=self,
        )

        if nombre is None:
            return

        codigo = simpledialog.askstring(
            "Código normalizado",
            "Código de tres letras (ejemplo: CHN):",
            parent=self,
        )

        if codigo is None:
            return

        self.establecer_equivalencia(
            nombre, codigo
        )

    def establecer_equivalencia(
        self, nombre, codigo, anterior=None
    ):
        try:
            nombre = normalizar_texto(nombre)
            codigo = normalizar_texto(codigo)

            if not nombre:
                raise ValueError(
                    "El nombre no puede estar vacío."
                )

            if (
                len(codigo) != 3
                or not codigo.isascii()
                or not codigo.isalpha()
            ):
                raise ValueError(
                    "El código debe contener tres "
                    "letras ASCII."
                )

            if (
                anterior in PAISES_REGIONALES
                or nombre in PAISES_REGIONALES
            ) and codigo != nombre:
                raise ValueError(
                    "No se pueden modificar los "
                    "códigos regionales oficiales."
                )

            catalogo = self.configuracion[
                "equivalencias_paises"
            ]

            if (
                nombre in catalogo
                and nombre != anterior
            ):
                raise ValueError(
                    "Esa equivalencia ya existe."
                )

            nuevo_catalogo = catalogo.copy()

            if anterior and anterior != nombre:
                nuevo_catalogo.pop(anterior, None)

            nuevo_catalogo[nombre] = codigo

            nueva_configuracion = {
                **self.configuracion,
                "equivalencias_paises": nuevo_catalogo,
            }

            validar_configuracion(
                nueva_configuracion
            )

            self.configuracion = nueva_configuracion
            self.actualizar_catalogo()

        except ValueError as error:
            messagebox.showerror(
                "Equivalencia inválida",
                str(error),
                parent=self,
            )

    def modificar_equivalencia(self):
        anterior = self.obtener_seleccion()

        if anterior is None:
            return

        codigo_actual = self.configuracion[
            "equivalencias_paises"
        ][anterior]

        nombre = simpledialog.askstring(
            "Modificar equivalencia",
            "Nombre o variante:",
            initialvalue=anterior,
            parent=self,
        )

        if nombre is None:
            return

        codigo = simpledialog.askstring(
            "Modificar código",
            "Código normalizado:",
            initialvalue=codigo_actual,
            parent=self,
        )

        if codigo is None:
            return

        self.establecer_equivalencia(
            nombre, codigo, anterior=anterior
        )

    def eliminar_equivalencia(self):
        nombre = self.obtener_seleccion()

        if nombre is None:
            return

        if nombre in PAISES_REGIONALES:
            messagebox.showwarning(
                "Operación no permitida",
                "No se pueden eliminar los "
                "códigos regionales oficiales.",
                parent=self,
            )
            return

        confirmar = messagebox.askyesno(
            "Eliminar equivalencia",
            f"¿Desea eliminar {nombre}?",
            parent=self,
        )

        if confirmar:
            catalogo = self.configuracion[
                "equivalencias_paises"
            ].copy()

            catalogo.pop(nombre, None)

            self.configuracion[
                "equivalencias_paises"
            ] = catalogo

            self.actualizar_catalogo()


    def guardar(self):
        """
        Guarda la configuración y solicita autorización
        cuando se intenta cambiar el umbral.
        """
        try:
            texto = self.umbral.get().strip()

            if not texto:
                raise ValueError(
                    "Debe indicar el umbral."
                )

            umbral = float(texto)

            nueva_configuracion = {
                **self.configuracion,
                "umbral_porcentaje": umbral,
            }

            validar_configuracion(
                nueva_configuracion
            )

            # Consultar el umbral actualmente guardado.
            configuracion_guardada = cargar_configuracion()

            umbral_actual = configuracion_guardada[
                "umbral_porcentaje"
            ]

            contrasena = None

            if umbral != umbral_actual:
                contrasena = simpledialog.askstring(
                    "Autorización administrativa",
                    "Está intentando modificar el "
                    "umbral de cumplimiento.\n\n"
                    f"Umbral actual: {umbral_actual:g}%\n"
                    f"Nuevo umbral: {umbral:g}%\n\n"
                    "Introduzca la contraseña administrativa:",
                    show="*",
                    parent=self,
                )

                if contrasena is None:
                    # El usuario canceló la autorización.
                    return

            guardar_configuracion(
                nueva_configuracion,
                contrasena_umbral=contrasena,
            )

            self.configuracion = nueva_configuracion

            messagebox.showinfo(
                "Configuración guardada",
                "Los parámetros se guardaron "
                "correctamente.",
                parent=self,
            )

            self.destroy()

        except (ValueError, PermissionError, OSError) as error:
            messagebox.showerror(
                "Error de configuración",
                str(error),
                parent=self,
            )
