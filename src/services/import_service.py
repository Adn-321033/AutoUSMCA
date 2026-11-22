from pathlib import Path
import pandas as pd


class ImportService:
    @staticmethod
    def cargar_archivo(ruta_archivo):
        """
        Carga un archivo XLSX o CSV y devuelve un DataFrame.
        """

        ruta = Path(ruta_archivo)

        if not ruta.exists():
            raise FileNotFoundError(
                "El archivo seleccionado no existe."
            )

        extension = ruta.suffix.lower()

        if extension == ".xlsx":
            dataframe = pd.read_excel(ruta)

        elif extension == ".csv":
            dataframe = pd.read_csv(ruta)

        else:
            raise ValueError(
                "Formato de archivo no compatible. "
                "Solo se permiten archivos XLSX o CSV."
            )

        return dataframe


    @staticmethod
    def cargar_reporte_aduanas(ruta_archivo):
        """
        Carga el reporte de materiales y productos
        de Aduanas conservando los códigos como texto.
        """
        ruta = Path(ruta_archivo)

        if not ruta.is_file():
            raise FileNotFoundError(
                "No se encontró el reporte de Aduanas."
            )

        extension = ruta.suffix.lower()

        tipos = {
            "PARTE": str,
            "FRACCION MX": str,
        }

        if extension == ".xlsx":
            return pd.read_excel(ruta, dtype=tipos)

        if extension == ".csv":
            return pd.read_csv(ruta, dtype=tipos)

        raise ValueError(
            "El reporte de Aduanas debe ser XLSX o CSV."
        )

    @staticmethod
    def cargar_reporte_finanzas(ruta_archivo):
        """
        Carga el reporte de costos de Finanzas
        sin interpretar la primera fila como encabezado.
        """
        ruta = Path(ruta_archivo)

        if not ruta.is_file():
            raise FileNotFoundError(
                "No se encontró el reporte de Finanzas."
            )

        extension = ruta.suffix.lower()

        if extension == ".xlsx":
            return pd.read_excel(
                ruta, header=None
            )

        if extension == ".csv":
            return pd.read_csv(
                ruta, header=None
            )

        raise ValueError(
            "El reporte de Finanzas debe ser XLSX o CSV."
        )
    