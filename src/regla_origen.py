
import math

import pandas as pd

from src.configuracion import cargar_configuracion


def verificar_regla_origen(materiales, financieros, configuracion=None):
    """
    Calcula el porcentaje no originario utilizando
    la lógica de P_WORKSHEET:

    I23 / G23

    G23 = materiales + mano de obra + costos indirectos.
    I23 = materiales no originarios.
    """

    if materiales.empty:
        raise ValueError("No existen materiales para calcular.")

    requeridas = ["COSTO_G", "COSTO_I"]
    if any(col not in materiales.columns for col in requeridas):
        raise ValueError("Faltan columnas de costos.")

    for campo in ["labor_day", "indirect_costs"]:
        if campo not in financieros:
            raise ValueError(f"Falta el valor {campo}.")

    costo_g = pd.to_numeric(
        materiales["COSTO_G"], errors="coerce"
    )

    costo_i = pd.to_numeric(
        materiales["COSTO_I"], errors="coerce"
    )

    if costo_g.isna().any():
        raise ValueError("Existen costos de materiales inválidos.")

    if (
        (costo_g < 0).any()
        or (costo_i.dropna() < 0).any()
    ):
        raise ValueError("Existen costos negativos.")

    labor = float(financieros["labor_day"])
    indirectos = float(financieros["indirect_costs"])

    if not all(math.isfinite(v) and v >= 0 for v in [labor, indirectos]):
        raise ValueError("Los costos financieros son inválidos.")

    total_materiales = float(costo_g.sum())
    costo_no_originario = float(costo_i.sum())

    costo_neto = total_materiales + labor + indirectos

    if costo_neto <= 0:
        raise ValueError("El costo neto debe ser mayor que cero.")

    if costo_no_originario > costo_neto + 1e-9:
        raise ValueError(
            "El costo no originario supera el costo neto."
        )

    proporcion = costo_no_originario / costo_neto
    porcentaje = proporcion * 100

        # Obtener el umbral configurado.
    if configuracion is None:
        configuracion = cargar_configuracion()

    umbral = configuracion["umbral_porcentaje"]

    # Determinar el cumplimiento.
    cumple = porcentaje <= umbral + 1e-10

    return {
        "total_materiales": total_materiales,
        "labor_day": labor,
        "indirect_costs": indirectos,
        "costo_neto": costo_neto,
        "costo_no_originario": costo_no_originario,
        "proporcion": proporcion,
        "porcentaje": porcentaje,
        "dentro_umbral_10": cumple,
        "cumple": cumple,
        "umbral_utilizado": umbral,
    }