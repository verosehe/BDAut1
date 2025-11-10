from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import calendar

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/"data/raw"
RAW.mkdir(parents=True, exist_ok=True)

# Configuración
N = 100_000
areas = ["Atención", "Soporte", "Ventas", "Marketing", "Logística"]
comentarios = ["Muy bien", "Regular", "Excelente", "Rápido", "Necesita mejora", ""]  # algunos vacíos

# Generar IDs
ids = [f"R{i:07d}" for i in range(1, N+1)]

# Generar fechas aleatorias dentro de un rango
now = datetime.now()
last_day = calendar.monthrange(now.year, now.month)[1]
start_date = datetime(int(now.strftime('%Y')), int(now.strftime('%m')), 1)
end_date = datetime(int(now.strftime('%Y')), int(now.strftime('%m')), last_day)
date_range = (end_date - start_date).days
fechas = [(start_date + timedelta(days=random.randint(0, date_range))).date() for _ in range(N)]

# Generar edades (18 a 70, algunos NaN)
edades = np.random.randint(18, 71, size=N)
mask_nan = np.random.rand(N) < 0.05  # 5% nulos
edades = edades.astype(float)
edades[mask_nan] = np.nan

# Generar áreas aleatorias
areas_random = np.random.choice(areas, size=N)

# Generar satisfacción (1-10, con algunos NS/NC y valores fuera de rango)
satisfaccion = np.random.randint(1, 11, size=N).astype(object)
mask_ns = np.random.rand(N) < 0.03  # 2% NS/NC
mask_out = np.random.rand(N) < 0.01  # 1% fuera de dominio (ej. 12, 15)
satisfacion_out_values = [12, 15]
satisfaccion[mask_ns] = "NS/NC"
satisfaccion[mask_out] = np.random.choice(satisfacion_out_values, size=mask_out.sum())

# Generar comentarios aleatorios
comentarios_random = np.random.choice(comentarios, size=N)

# Crear DataFrame
df = pd.DataFrame({
    "id_respuesta": ids,
    "fecha": fechas,
    "edad": edades,
    "area": areas_random,
    "satisfaccion": satisfaccion,
    "comentario": comentarios_random
})

# Guardar Excel
file_name = RAW/f"encuestas_{datetime.now().strftime('%Y%m')}.xlsx"
df.to_excel(file_name, index=False)
print("Excel generado")
