# Lecciones aprendidas

## Qué salió bien
- El pipeline de ingesta funciona con formato `CSV` y mantiene trazabilidad (`_source_file`, `_ingest_ts`, `_batch_id`).  
- La limpieza y validación detecta y separa correctamente registros inválidos hacia cuarentena.  
- Deduplicación “último gana” asegura consistencia en los datos.  
- Persistencia en **Parquet** y **SQLite** permite consultas rápidas y generación de reportes reproducibles.  
- Reporte Markdown automático con KPIs por área y evolución mensual facilita la toma de decisiones.

## Qué mejorar
- Incorporar batch_id real calculado a partir de hash de archivo para mejorar idempotencia.  
- Alertas automáticas si hay un incremento inusual de registros en cuarentena.  
- Optimizar lectura y escritura de Parquet para datasets muy grandes (>1M filas).  
- Documentar mejor supuestos de negocio (p. ej., tratamiento de NS/NC en satisfacción).  

## Siguientes pasos
- Implementar monitorización de tendencias de satisfacción por área.  
- Analizar motivos de cuarentena y proponer limpieza automática de errores comunes.  
- Generar dashboard visual con KPIs diarios/mensuales.  


