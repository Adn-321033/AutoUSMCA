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