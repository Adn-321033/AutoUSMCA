
import pandas as pd
import pytest
from pypdf import PdfReader

from src.generador_pdf import generar_reporte_pdf


@pytest.fixture
def datos_pdf():
    materiales = pd.DataFrame({
        "PARTE": ["MAT001", "MAT002"],
        "ORIGEN": ["MEX", "CHN"],
        "VALOR US": [60.0, 20.0],
        "COSTO_I": [float("nan"), 20.0],
        "KILOGRAMOS IMPORTACION": [0.5, 0.2],
    })

    financieros = {
        "labor_day": 10.0,
        "indirect_costs": 10.0,
    }

    resultado = {
        "total_materiales": 80.0,
        "costo_neto": 100.0,
        "costo_no_originario": 20.0,
        "porcentaje": 20.0,
    }

    return materiales, financieros, resultado


def test_crear_pdf(tmp_path, datos_pdf):
    materiales, financieros, resultado = datos_pdf

    ruta = tmp_path / "reporte.pdf"

    generar_reporte_pdf(
        "CT0143", materiales, financieros,
        resultado, ruta
    )

    assert ruta.exists()
    assert ruta.stat().st_size > 0


def test_contenido_pdf(tmp_path, datos_pdf):
    materiales, financieros, resultado = datos_pdf

    ruta = tmp_path / "contenido.pdf"

    generar_reporte_pdf(
        "CT0143", materiales, financieros,
        resultado, ruta
    )

    lector = PdfReader(str(ruta))
    texto = "\n".join(
        pagina.extract_text() or ""
        for pagina in lector.pages
    )

    assert "CT0143" in texto
    assert "MAT001" in texto
    assert "MAT002" in texto
    assert "20.00000%" in texto


def test_pdf_sin_materiales(tmp_path, datos_pdf):
    _, financieros, resultado = datos_pdf

    with pytest.raises(
        ValueError, match="No existen materiales"
    ):
        generar_reporte_pdf(
            "CT0143",
            pd.DataFrame(),
            financieros,
            resultado,
            tmp_path / "invalido.pdf",
        )


def test_pdf_columnas_incompletas(tmp_path, datos_pdf):
    materiales, financieros, resultado = datos_pdf

    materiales = materiales.drop(columns=["ORIGEN"])

    with pytest.raises(ValueError, match="Faltan columnas"):
        generar_reporte_pdf(
            "CT0143",
            materiales,
            financieros,
            resultado,
            tmp_path / "incompleto.pdf",
        )
