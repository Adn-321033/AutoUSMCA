import sqlite3
from pathlib import Path


DB_PATH = Path("database") / "autousmca.db"


def crear_base_datos():
    """Crea la base de datos y las tablas iniciales de AutoUSMCA."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ejecuciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_ejecucion DATETIME DEFAULT CURRENT_TIMESTAMP,
            archivo_costos TEXT,
            archivo_consumos TEXT,
            total_partes INTEGER DEFAULT 0,
            partes_cumplen INTEGER DEFAULT 0,
            partes_no_cumplen INTEGER DEFAULT 0,
            estado TEXT DEFAULT 'FINALIZADA'
        )
        """
    )

    conexion.commit()
    conexion.close()

    print(f"Base de datos creada correctamente en: {DB_PATH}")


if __name__ == "__main__":
    crear_base_datos()