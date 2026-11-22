
import pytest

from src.configuracion import (
    cargar_configuracion,
    guardar_configuracion,
    validar_configuracion,
    normalizar_pais,
    configuracion_predeterminada,
)


def test_configuracion_predeterminada(tmp_path):
    ruta = tmp_path / "configuracion.json"

    config = cargar_configuracion(ruta)

    assert config["umbral_porcentaje"] == 10.0
    assert config["equivalencias_paises"]["MEX"] == "MEX"


def test_guardar_y_cargar_configuracion(tmp_path):
    ruta = tmp_path / "configuracion.json"

    config = configuracion_predeterminada()
    config["umbral_porcentaje"] = 8.5

    guardar_configuracion(config, ruta)

    recuperada = cargar_configuracion(ruta)

    assert recuperada["umbral_porcentaje"] == 8.5


def test_normalizar_paises():
    config = configuracion_predeterminada()

    assert normalizar_pais("México", config) == "MEX"
    assert normalizar_pais("mx", config) == "MEX"
    assert normalizar_pais("United States", config) == "USA"
    assert normalizar_pais("Canadá", config) == "CAN"
    assert normalizar_pais("CHN", config) == "CHN"


def test_agregar_equivalencia(tmp_path):
    ruta = tmp_path / "configuracion.json"

    config = configuracion_predeterminada()
    config["equivalencias_paises"]["ALEMANIA"] = "DEU"

    guardar_configuracion(config, ruta)

    recuperada = cargar_configuracion(ruta)

    assert normalizar_pais(
        "Alemania", recuperada
    ) == "DEU"


@pytest.mark.parametrize(
    "umbral",
    [-1, 101, "diez", None, float("nan")],
)
def test_umbral_invalido(umbral):
    config = configuracion_predeterminada()
    config["umbral_porcentaje"] = umbral

    with pytest.raises(ValueError):
        validar_configuracion(config)


def test_pais_invalido():
    config = configuracion_predeterminada()

    with pytest.raises(ValueError):
        normalizar_pais("PAIS DESCONOCIDO", config)


def test_configuracion_json_invalida(tmp_path):
    ruta = tmp_path / "configuracion.json"
    ruta.write_text("{archivo incorrecto}", encoding="utf-8")

    with pytest.raises(ValueError):
        cargar_configuracion(ruta)
