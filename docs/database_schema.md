# Esquema inicial de la base de datos AutoUSMCA

La base de datos local utiliza SQLite.

## Tabla: ejecuciones

Campos principales:

- id
- fecha_ejecucion
- archivo_costos
- archivo_consumos
- total_partes
- partes_cumplen
- partes_no_cumplen
- estado

Esta tabla servirá para almacenar el historial de ejecuciones realizadas por AutoUSMCA.