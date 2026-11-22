
from pathlib import Path

from src.procesamiento_usmca import procesar_producto


BASE_DIR = Path(__file__).resolve().parent

resultado = procesar_producto(
    "CT0143",
    BASE_DIR
)

calculo = resultado["resultado"]

print("\n=== RESULTADOS AUTOUSMCA ===")
print("Producto:", resultado["producto"])
print(
    "Materiales originales:",
    resultado["materiales_originales"]
)
print(
    "Materiales consolidados:",
    resultado["materiales_consolidados"]
)

print(f"Total materiales: {calculo['total_materiales']:.5f}")
print(f"Labor Day: {calculo['labor_day']:.5f}")
print(f"Indirect Costs: {calculo['indirect_costs']:.5f}")
print(f"Costo neto: {calculo['costo_neto']:.5f}")
print(
    f"Costo no originario: "
    f"{calculo['costo_no_originario']:.5f}"
)
print(f"Porcentaje: {calculo['porcentaje']:.5f}%")

print("\nArchivo generado:", resultado["archivo"])

print("Reporte PDF:", resultado["archivo_pdf"])