---
title: "Definición de métricas y tablas oro"
owner: "Verónica Serrano Hernández"
periodicidad: "diaria"
version: "1.0.0"
---

# Modelo de negocio (capa oro)

## Tablas oro
- **clean_ventas** (fuente): granularidad **respuesta individual**
- **ventas_diarias** (vista): granularidad **día**

## Métricas (KPI)
- **Promedio satisfacción**: Σ(`satisfaccion`) / nº respuestas  válidas
- **Número de respuestas**: total de filas válidas por día
- **Área líder**: `area` con mayor satisfacción promedio

## Supuestos
- `satisfacción` entre 1 y 10
- Nulos o NS/NC → cuarentena, no se incluyen en KPIs
- Dedupe “último gana” por `_ingest_ts` y `id_respuesta`

## Consultas base (SQL conceptual)
```sql
-- Promedio de satisfacción y número de respuestas por día
SELECT fecha, 
       COUNT(*) AS num_respuestas,
       AVG(satisfaccion) AS prom_satisfaccion
FROM clean_encuestas
GROUP BY fecha;

-- Área líder por número de respuestas
SELECT area, COUNT(*) AS num_respuestas
FROM clean_encuestas
GROUP BY area
ORDER BY num_respuestas DESC
LIMIT 1;

-- Área líder por satisfacción promedio
SELECT area, AVG(satisfaccion) AS prom_satisfaccion
FROM clean_encuestas
GROUP BY area
ORDER BY prom_satisfaccion DESC
LIMIT 1;
s
```
