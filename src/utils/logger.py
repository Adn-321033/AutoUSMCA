
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler


NOMBRE_LOGGER = "AutoUSMCA"

RUTA_LOG = (
    Path(__file__).resolve().parents[2]
    / "logs"
    / "autousmca.log"
)


def configurar_logger(ruta_log=None):
    """
    Configura el sistema de bitácora de AutoUSMCA.

    Registra mensajes informativos, advertencias
    y errores en un archivo local.
    """

    ruta = Path(ruta_log) if ruta_log else RUTA_LOG
    ruta = ruta.resolve()

    ruta.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    logger = logging.getLogger(NOMBRE_LOGGER)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Evitar duplicar manejadores al configurar
    # el logger varias veces.
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    manejador = RotatingFileHandler(
        ruta,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )

    formato = logging.Formatter(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    manejador.setFormatter(formato)

    logger.addHandler(manejador)

    return logger


def obtener_logger():
    """
    Devuelve el logger configurado.
    """

    logger = logging.getLogger(NOMBRE_LOGGER)

    if not logger.handlers:
        return configurar_logger()

    return logger
