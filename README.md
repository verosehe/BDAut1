# project/ — Ejecución técnica (Parquet + SQLite)

## Flujo (mínimo viable)
1. **Ingesta**: lee el excel `xlsx`, añade `_source_file` y `_ingest_ts` y coerción de tipos.
2. **Limpieza**: rangos/dominos básicos, cuarentena, dedupe “último gana”.
3. **Persistencia**: 
   - **Parquet** (`output/parquet/clean_encuestas.parquet`)
   - **SQLite** (`output/encuestas.db`) con tablas y vistas (opcional, ya integrado)
4. **Reporte**: **releído desde Parquet** (fuente de verdad) → `output/reporte.md`.

## Comandos
```bash
pip install -r requirements.txt
python ingest/get_data.py      # opcional (genera un CSV de ejemplo)
python ingest/run.py           # ejecuta todo: parquet + sqlite + reporte.md
```
