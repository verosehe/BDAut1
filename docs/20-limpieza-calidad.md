# Reglas de limpieza y calidad

## Tipos y formatos
- `fecha`: ISO (`YYYY-MM-DD`)
- `edad`: entero ≥ 0
- `satisfaccion`: decimal entre 1 y 10
- `area` y `comentario`: texto 

## Nulos
- Campos obligatorios: (`fecha`, `id_respuesta`, `area`, `satisfaccion`)
- Tratamiento: filas con valores inválidos o nulos en campos obligatorios → **quarantine** con motivo documentado

## Rangos y dominios
- `edad >= 0` (opcional, si se tiene)
- `satisfaccion`entre 1 y 10
- `area` corresponde a los valores conocidos de departamentos o áreas

## Deduplicación
- Clave natural: `(fecha, id_respuesta)`
- Política: **último gana** por `_ingest_ts` al eliminar duplicados

## Estandarización de texto
- `trim` de espacios al inicio/final
- Eliminación de tildes `á → a`
- Capitalización consistente: `area` en título, `comentario` sin capitalizar

## Trazabilidad
- Mantener `_ingest_ts`, `_source_file`, `_batch_id` en todas las capas (raw, clean, quarantine)

## QA rápida
- % de filas a quarantine (fuera de rango o nulas)
- Conteos por día vs. esperado
- Validación de dominios y rangos de satisfacción y edad
