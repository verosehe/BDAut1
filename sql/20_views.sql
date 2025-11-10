-- Vista de satisfacción promedio por área
CREATE VIEW IF NOT EXISTS avg_satisf_area AS
SELECT area, ROUND(AVG(satisfaccion),2) AS satisf_prom
FROM clean_encuestas
GROUP BY area;

-- Vista de evolución mensual de satisfacción
CREATE VIEW IF NOT EXISTS monthly_satisf AS
SELECT strftime('%Y-%m', fecha) AS mes, area, ROUND(AVG(satisfaccion),2) AS satisf_prom
FROM clean_encuestas
GROUP BY mes, area;
