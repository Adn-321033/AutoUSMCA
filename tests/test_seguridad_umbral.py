
import json

import pytest

from src.seguridad_umbral import (
    crear_contrasena,
    verificar_contrasena,
)


def test_crear_y_verificar_contrasena(tmp_path):
    ruta = tmp_path / "seguridad.json"

    crear_contrasena(
        "ClaveAdministrativa123!",
        ruta,
    )

    assert verificar_contrasena(
        "ClaveAdministrativa123!",
        ruta,
    )


def test_contrasena_incorrecta(tmp_path):
    ruta = tmp_path / "seguridad.json"

    crear_contrasena(
        "ClaveAdministrativa123!",
        ruta,
    )

    assert not verificar_contrasena(
        "ContrasenaIncorrecta",
        ruta,
    )


def test_no_guardar_contrasena_plana(tmp_path):
    ruta = tmp_path / "seguridad.json"

    crear_contrasena(
        "ClaveAdministrativa123!",
        ruta,
    )

    contenido = ruta.read_text(
        encoding="utf-8"
    )

    assert "ClaveAdministrativa123!" not in contenido

    datos = json.loads(contenido)

    assert "sal" in datos
    assert "hash" in datos


def test_no_permitir_reinicializacion(tmp_path):
    ruta = tmp_path / "seguridad.json"

    crear_contrasena(
        "ClaveAdministrativa123!",
        ruta,
    )

    with pytest.raises(ValueError):
        crear_contrasena(
            "OtraClaveAdministrativa123!",
            ruta,
        )


def test_seguridad_no_configurada(tmp_path):
    ruta = tmp_path / "no_existe.json"

    with pytest.raises(ValueError):
        verificar_contrasena(
            "ClaveAdministrativa123!",
            ruta,
        )
