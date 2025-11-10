# Diseño de ingestión

## Resumen
Los datos de encuestas se ingieren desde archivos colocados en la carpeta data/drops/ de manera diaria. Cada ingesta genera un lote único y controlado, con validación mínima de columnas y tipos. Se garantiza idempotencia y trazabilidad de cada registro.

## Fuente
- **Origen:** data/drops/encuestas_*.xlsx / *.csv
- **Formato:** Excel (.xlsx), CSV
- **Frecuencia:** diaria (batch)

## Estrategia
- **Modo:** `batch`
- **Incremental:** se procesan únicamente los archivos nuevos o modificados, evitando duplicados por _batch_id
- **Particionado:** se guardan los datos limpios en Parquet particionado opcionalmente por mes (YYYY/MM) para facilitar análisis posteriores

## Idempotencia y deduplicación
- **batch_id:** `hash(nombre_archivo + tamaño + mtime)`
- **clave natural:** `(fecha, id_respuesta)`
- **Política:** “último gana por _ingest_ts” al eliminar duplicados

## Checkpoints y trazabilidad
- **checkpoints/offset:** cada fila mantiene _ingest_ts (fecha y hora exacta de ingesta), _source_file (archivo de origen), _batch_id (identificador del lote)
- **trazabilidad:** `_ingest_ts`, `_source_file`, `_batch_id`
- **DLQ/quarantine:** registros con valores fuera de rango en satisfaccion se guardan en output/quarantine/out_of_range.encuestas.parquet con motivo documentado

## SLA
- **Disponibilidad:** ingesta diaria
- **Alertas:** logs de errores y CSV/Parquet de cuarentena para revisar manualmente

## Riesgos / Antipatrones
- Intentar hacer micro-batch con segundos de diferencia → **no encaja** en este flujo
- Falta de clave natural o _ingest_ts → riesgo de duplicados y pérdida de trazabilidad
