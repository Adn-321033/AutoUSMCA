
import sqlite3
from pathlib import Path


DB_PATH = Path("database") / "autousmca.db"


def obtener_conexion(ruta_db=None):
    """Obtiene una conexión a la base de datos SQLite."""

    ruta = Path(ruta_db) if ruta_db is not None else DB_PATH
    ruta.parent.mkdir(parents=True, exist_ok=True)

    conexion = sqlite3.connect(ruta)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")

    return conexion


def crear_base_datos(ruta_db=None):
    """Crea o actualiza las tablas de AutoUSMCA."""

    conexion = obtener_conexion(ruta_db)

    try:
        cursor = conexion.cursor()

        # Tabla principal de ejecuciones
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ejecuciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_ejecucion DATETIME
                    DEFAULT CURRENT_TIMESTAMP,
                archivo_costos TEXT,
                archivo_consumos TEXT,
                total_partes INTEGER DEFAULT 0,
                partes_cumplen INTEGER DEFAULT 0,
                partes_no_cumplen INTEGER DEFAULT 0,
                estado TEXT DEFAULT 'FINALIZADA'
            )
            """
        )

        # Actualizar la tabla anterior sin eliminar datos
        columnas = [
            fila["name"]
            for fila in cursor.execute(
                "PRAGMA table_info(ejecuciones)"
            ).fetchall()
        ]

        if "usuario" not in columnas:
            cursor.execute(
                """
                ALTER TABLE ejecuciones
                ADD COLUMN usuario TEXT
                """
            )

        # Tabla de resultados por producto terminado
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS resultados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ejecucion_id INTEGER NOT NULL,
                numero_parte TEXT NOT NULL,
                total_materiales REAL NOT NULL,
                labor_day REAL NOT NULL,
                indirect_costs REAL NOT NULL,
                costo_neto REAL NOT NULL,
                costo_no_originario REAL NOT NULL,
                porcentaje_no_regional REAL NOT NULL,
                cumple INTEGER NOT NULL
                    CHECK (cumple IN (0, 1)),
                cantidad_materiales_originales INTEGER,
                cantidad_materiales_consolidados INTEGER,
                archivo_excel TEXT,
                archivo_pdf TEXT,

                FOREIGN KEY (ejecucion_id)
                    REFERENCES ejecuciones(id)
                    ON DELETE CASCADE
            )
            """
        )

        # Tabla de materiales utilizados en cada cálculo
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS detalle_materiales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resultado_id INTEGER NOT NULL,
                numero_parte TEXT NOT NULL,
                descripcion TEXT,
                fraccion_arancelaria TEXT,
                pais_origen TEXT NOT NULL,
                es_regional INTEGER NOT NULL
                    CHECK (es_regional IN (0, 1)),
                kilogramos REAL NOT NULL,
                costo_total REAL NOT NULL,
                costo_no_regional REAL NOT NULL,

                FOREIGN KEY (resultado_id)
                    REFERENCES resultados(id)
                    ON DELETE CASCADE
            )
            """
        )

        # Índices para facilitar consultas
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_ejecuciones_fecha
            ON ejecuciones(fecha_ejecucion)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_ejecuciones_usuario
            ON ejecuciones(usuario)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_resultados_parte
            ON resultados(numero_parte)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_resultados_ejecucion
            ON resultados(ejecucion_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_materiales_resultado
            ON detalle_materiales(resultado_id)
            """
        )

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()

    ruta = Path(ruta_db) if ruta_db is not None else DB_PATH
    print(f"Base de datos creada correctamente en: {ruta}")


if __name__ == "__main__":
    crear_base_datos()
