
import logging

from src.utils.logger import (
    configurar_logger,
    obtener_logger,
)


def test_crear_archivo_bitacora(tmp_path):
    ruta = tmp_path / "autousmca.log"

    logger = configurar_logger(ruta)

    logger.info("Inicio de prueba")

    assert ruta.exists()
    assert "Inicio de prueba" in ruta.read_text(
        encoding="utf-8"
    )


def test_registrar_error(tmp_path):
    ruta = tmp_path / "errores.log"

    logger = configurar_logger(ruta)

    logger.error("Archivo inválido")

    contenido = ruta.read_text(encoding="utf-8")

    assert "ERROR" in contenido
    assert "Archivo inválido" in contenido


def test_registrar_advertencia(tmp_path):
    ruta = tmp_path / "advertencias.log"

    logger = configurar_logger(ruta)

    logger.warning("Registro incompleto")

    contenido = ruta.read_text(encoding="utf-8")

    assert "WARNING" in contenido
    assert "Registro incompleto" in contenido


def test_no_duplicar_handlers(tmp_path):
    ruta = tmp_path / "autousmca.log"

    configurar_logger(ruta)
    logger = configurar_logger(ruta)

    assert len(logger.handlers) == 1


def test_obtener_logger(tmp_path):
    ruta = tmp_path / "autousmca.log"

    configurar_logger(ruta)
    logger = obtener_logger()

    assert isinstance(logger, logging.Logger)

    logger.info("Mensaje de verificación")

    assert "Mensaje de verificación" in ruta.read_text(
        encoding="utf-8"
    )
