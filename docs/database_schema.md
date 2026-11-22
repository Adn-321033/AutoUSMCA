
# Esquema de la base de datos AutoUSMCA

## 1. Descripción general

AutoUSMCA utiliza SQLite como sistema de gestión de base de datos local para almacenar el historial de las ejecuciones realizadas.

La base de datos se encuentra en:

`database/autousmca.db`

El módulo de historial permite conservar los resultados de los cálculos y recuperar información de ejecuciones anteriores sin necesidad de procesar nuevamente los archivos originales.

## 2. Tabla: ejecuciones

Almacena la información general de cada procesamiento.

| Campo | Descripción |
|---|---|
| id | Identificador único de la ejecución. |
| fecha_ejecucion | Fecha y hora del procesamiento. |
| usuario | Usuario que realizó la ejecución. |
| archivo_costos | Ruta del reporte de Finanzas. |
| archivo_consumos | Ruta del reporte de Aduanas. |
| total_partes | Cantidad de productos procesados. |
| partes_cumplen | Productos que cumplen con el umbral. |
| partes_no_cumplen | Productos que no cumplen. |
| estado | Estado de la ejecución. |

La llave primaria es `id`.

## 3. Tabla: resultados

Almacena los cálculos realizados para cada producto terminado.

| Campo | Descripción |
|---|---|
| id | Identificador del resultado. |
| ejecucion_id | Identificador de la ejecución relacionada. |
| numero_parte | Número de parte del producto terminado. |
| total_materiales | Costo total de materiales. |
| labor_day | Costo de mano de obra. |
| indirect_costs | Costos indirectos. |
| costo_neto | Costo total del producto. |
| costo_no_originario | Costo de materiales no originarios. |
| porcentaje_no_regional | Porcentaje calculado de contenido no regional. |
| cumple | Resultado de cumplimiento: 1 o 0. |
| cantidad_materiales_originales | Registros originales de materiales. |
| cantidad_materiales_consolidados | Materiales después de la consolidación. |
| archivo_excel | Ruta del reporte Excel generado. |
| archivo_pdf | Ruta del reporte PDF generado. |

La llave primaria es `id` y la llave foránea es `ejecucion_id`.

## 4. Tabla: detalle_materiales

Almacena la información de las materias primas utilizadas en cada cálculo.

| Campo | Descripción |
|---|---|
| id | Identificador del material registrado. |
| resultado_id | Identificador del resultado relacionado. |
| numero_parte | Número de parte de la materia prima. |
| descripcion | Descripción del material. |
| fraccion_arancelaria | Fracción arancelaria del material. |
| pais_origen | País de origen del material. |
| es_regional | Clasificación regional: 1 o 0. |
| kilogramos | Peso del material. |
| costo_total | Costo total del material. |
| costo_no_regional | Costo no regional correspondiente. |

La llave primaria es `id` y la llave foránea es `resultado_id`.

## 5. Relaciones entre las tablas

Las tablas presentan las siguientes relaciones:

- Una ejecución puede contener varios resultados.
- Cada resultado pertenece a una ejecución.
- Un resultado puede contener varios materiales.
- Cada material registrado pertenece a un resultado.

Estas relaciones se implementan mediante llaves foráneas de SQLite.

## 6. Módulo de historial

El módulo se encuentra en:

`src/repositories/historial_repository.py`

Implementa las siguientes funciones:

### guardar_ejecucion()

Registra una ejecución completa, incluyendo sus resultados y materiales. Utiliza una transacción para evitar almacenar información incompleta.

### consultar_ejecuciones()

Permite consultar las ejecuciones almacenadas utilizando filtros opcionales por fecha, usuario y número de parte.

### obtener_ejecucion()

Recupera una ejecución anterior, incluyendo los resultados de los productos y el detalle de sus materiales.

## 7. Pruebas realizadas

El módulo fue verificado mediante seis pruebas automatizadas desarrolladas con pytest.

Las pruebas comprobaron:

1. Almacenamiento de una ejecución.
2. Recuperación de materiales.
3. Consulta por número de parte.
4. Consulta por usuario.
5. Recuperación de ejecuciones inexistentes.
6. Integridad de las transacciones ante errores.

Las seis pruebas se ejecutaron satisfactoriamente.

Adicionalmente, se realizó una ejecución con información real del producto terminado CT0143, que generó reportes Excel y PDF y registró la ejecución en SQLite.

## 8. Consideraciones de almacenamiento

La base de datos funciona localmente y no requiere conexión a Internet.

Las operaciones de inserción utilizan transacciones para mantener la integridad de la información.

Las relaciones entre las tablas permiten conservar los resultados de las ejecuciones y facilitar su consulta posterior.

El archivo de base de datos se excluye del repositorio Git mediante `.gitignore`, debido a que puede contener información empresarial.
