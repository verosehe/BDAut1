from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
import numpy as np
import sqlite3
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw"
OUT = ROOT / "output"
DROPS = ROOT / "data"/ "drops" / datetime.now().strftime("%Y-%m-%d")
DROPS.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "parquet").mkdir(parents=True, exist_ok=True)
(OUT / "quality").mkdir(parents=True, exist_ok=True)
(OUT / "quarantine").mkdir(parents=True, exist_ok=True)



#######################################################################################################################
# 1) Ingesta

# Mapa de columnas esperadas
COLUMN_MAP = {
    "IdRespuesta": "id_respuesta",
    "Fecha": "fecha",
    "Edad": "edad",
    "Area": "area",
    "Satisfaccion": "satisfaccion",
    "Comentario": "comentario",
}

EXPECTED_COLUMNS = ["id_respuesta", "fecha", "edad", "area", "satisfaccion", "comentario"]

# === Ingesta ===
files = sorted(DATA.glob("encuestas_*.xlsx"))
ingested = []

for f in files:
    print(f" Leyendo {f.name} ...")
    df = pd.read_excel(f, dtype=str)  # leer como texto

    # Renombrar columnas según el mapa
    df.rename(columns=COLUMN_MAP, inplace=True)

    # Asegurar que existan todas las columnas esperadas
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = None

    # Ordenar columnas y añadir metadatos
    df = df[EXPECTED_COLUMNS]

    df["_source_file"] = f.name
    df["_ingest_ts"] = datetime.now(timezone.utc).isoformat()
    
    ingested.append(df)

    # Coerción básica de tipos
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["edad"] = pd.to_numeric(df["edad"], errors="coerce")
    df["satisfaccion"] = pd.to_numeric(df["satisfaccion"], errors="coerce")
    
    if ingested:
       raw_df = pd.concat(ingested, ignore_index=True)
    else:
       raw_df = pd.DataFrame(columns=EXPECTED_COLUMNS + ["_source_file","_ingest_ts"])

    # Guardar CSV homogéneo
    out_path = DROPS / f"{f.stem}.csv"
    df.to_csv(out_path, index=False)
    print(f" Guardado {out_path.name}")
    ingested.append(df)

# === Concatenar todo si se desea un batch único ===
# if ingested:
#     batch_df = pd.concat(ingested, ignore_index=True)
#     batch_df.to_csv(DROPS / "encuestas_batch.csv", index=False)
#     print(f" Batch completo guardado en {DROPS/'encuestas_batch.csv'}")
# else:
#     print(" No se encontraron archivos nuevos para procesar.")

##########################################################################################################################################3
#Limpieza
# Seleccionar la carpeta más reciente (última ingesta)
latest_drop = DROPS
print(f" Procesando limpieza para batch: {latest_drop.name}")

# === Lectura de datos homogéneos ===
files = list(latest_drop.glob("*.csv"))
if not files:
    raise FileNotFoundError("No se encontraron CSV en la carpeta de drops más reciente.")

df_raw = pd.concat([pd.read_csv(f, dtype=str) for f in files], ignore_index=True)
print(f"{len(df_raw)} registros cargados desde {len(files)} archivos.")

# # === Funciones auxiliares ===

def normalize_text(s, title_case=True):
    """Normaliza texto: elimina tildes, espacios extra y opcional a título"""
    if pd.isna(s):
        return s
    s = str(s).strip()
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode("utf-8")
    return s.title() if title_case else s

def parse_satisfaccion(x):
    """
    Convierte NS/NC a NaN
    Devuelve float si es numérico, incluso fuera de rango
    """
    if isinstance(x, str):
        v = x.strip().upper()
        if v in ["NS/NC", "NO SABE", "NO CONTESTA"]:
            return np.nan
    try:
        return float(x)
    except:
        return np.nan

# Copiar raw_df
df = raw_df.copy()

# Asegurar columnas
for c in ["id_respuesta","fecha","edad","area","satisfaccion","comentario"]:
    if c not in df.columns:
        df[c] = None

# Coerción de tipos
df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce").dt.date
df["edad"] = pd.to_numeric(df["edad"], errors="coerce")
df["satisfaccion_raw"] = df["satisfaccion"]  # para cuarentena
df["satisfaccion"] = df["satisfaccion"].apply(parse_satisfaccion)
df["area"] = df["area"].apply(normalize_text)
df["comentario"] = df["comentario"].fillna("").apply(lambda x: normalize_text(x, title_case=False))

# === Validación ===
valid_mask = (
    df["fecha"].notna()
    & df["id_respuesta"].notna() & (df["id_respuesta"] != "")
    & df["area"].notna() & (df["area"] != "")
    & df["satisfaccion"].between(1,10)  # válidos entre 1-10
)

# Filas válidas
clean = df.loc[valid_mask].copy()

# Cuarentena: valores numéricos fuera de rango, excluye NS/NC (NaN)
quarantine = df.loc[~valid_mask & df["satisfaccion_raw"].apply(lambda x: str(x).replace('.','',1).isdigit())].copy()

# Dedupe
if not clean.empty:
    clean = clean.sort_values("_ingest_ts").drop_duplicates(subset=["id_respuesta"], keep="last")

# === Informe de calidad ===
quality = {
    "campo": ["fecha", "edad", "area", "satisfaccion", "comentario"],
    "nulos": [
        df["fecha"].isna().sum(),
        df["edad"].isna().sum(),
        df["area"].isna().sum(),
        df["satisfaccion"].isna().sum(),
        df["comentario"].isna().sum(),
    ],
    "fuera_de_dominio": [
        0,  # fecha no tiene dominio
        0,  # edad no validada aquí
        0,  # area no validada aquí
        ((df["satisfaccion"].notna()) & (~df["satisfaccion"].between(1,10))).sum(),
        0,
    ],
}

df_quality = pd.DataFrame(quality)
quality_path = OUT / "quality" / "informe_de_calidad.xlsx"
df_quality.to_excel(quality_path, index=False)
print(f"Informe de calidad guardado en {quality_path}")    

#############################################################################################################
# 3) Persistencia: Parquet (fuente de reporte) + SQLite (opcional integrado)
PARQUET_FILE = OUT / "parquet" / "clean.encuestas.parquet"
if not clean.empty:
    clean.to_parquet(PARQUET_FILE, index=False)

quarantine_file = OUT / "quarantine" / "out_of_range.encuestas.parquet"
quarantine_file.parent.mkdir(parents=True, exist_ok=True)
if not quarantine.empty:
    quarantine.to_parquet(quarantine_file, index=False)

print(f"Registros válidos: {len(clean)}, cuarentena: {len(quarantine)}, totales: {len(df)}")

#SQLite
DB = OUT / "encuestas.db"
con = sqlite3.connect(DB)
con.executescript((ROOT / "sql" / "00_schema.sql").read_text(encoding="utf-8"))

# === RAW ===
if not df.empty:
    df_raw_sql = df[[
        "id_respuesta",
        "fecha",
        "edad",
        "area",
        "satisfaccion",
        "comentario",
        "_ingest_ts",
        "_source_file"
    ]].copy()
    df_raw_sql["_batch_id"] = "demo"  # simplificado
    df_raw_sql.to_sql("raw_encuestas", con, if_exists="append", index=False)

# === CLEAN ===
if not clean.empty:
    clean.to_sql("clean_encuestas", con, if_exists="replace", index=False)

# === QUARANTINE ===
if not quarantine.empty:
    quarantine.to_sql("quarantine_encuestas", con, if_exists="replace", index=False)

# === Vistas o scripts adicionales ===
con.executescript((ROOT / "sql" / "20_views.sql").read_text(encoding="utf-8"))

con.close()



# ##########################################################################################################################################
# 4) Reporte releído desde PARQUET
if PARQUET_FILE.exists():
    clean_rep = pd.read_parquet(PARQUET_FILE)
else:
    clean_rep = pd.DataFrame(columns=["fecha","id_respuesta","edad","area","satisfaccion","comentario","_ingest_ts"])

if not clean_rep.empty:
    total_encuestas = len(clean_rep)
    satisf_prom = float(clean_rep["satisfaccion"].mean())
    
    # Área con mayor satisfacción promedio
    area_lider = clean_rep.groupby("area")["satisfaccion"].mean().idxmax() if not clean_rep["area"].dropna().empty else "—"
    satisf_area = clean_rep.groupby("area")["satisfaccion"].mean().round(2)
    
    # Evolución mensual
    clean_rep["mes"] = pd.to_datetime(clean_rep["fecha"]).dt.to_period("M")
    evolucion = clean_rep.groupby(["mes","area"])["satisfaccion"].mean().unstack(fill_value=0).round(2)
    
    periodo_ini = str(clean_rep["fecha"].min())
    periodo_fin = str(clean_rep["fecha"].max())
else:
    total_encuestas = 0
    satisf_prom = 0.0
    area_lider = "—"
    satisf_area = pd.Series(dtype=float)
    evolucion = pd.DataFrame()
    periodo_ini = "—"
    periodo_fin = "—"

report = (
    "# Reporte UT1 · Encuestas\n"
    f"**Periodo:** {periodo_ini} a {periodo_fin} · **Fuente:** clean_encuestas (Parquet) · **Generado:** {datetime.now(timezone.utc).isoformat()}\n\n"
    "## 1. Titular\n"
    f"Total encuestas: {total_encuestas}; área con mayor satisfacción promedio: {area_lider}.\n\n"
    "## 2. KPIs por área\n"
    f"{(satisf_area.to_markdown() if not satisf_area.empty else '_(sin datos)_')}\n\n"
    "## 3. Evolución mensual por área\n"
    f"{(evolucion.to_markdown() if not evolucion.empty else '_(sin datos)_')}\n\n"
    "## 4. Calidad y cobertura\n"
    f"- Filas bronce: {len(df)} · Plata (válidas): {len(clean)} · Cuarentena: {len(quarantine)}\n\n"
    "## 5. Persistencia\n"
    f"- Parquet: {PARQUET_FILE}\n"
    f"- SQLite : {DB} (tablas: raw_encuestas, clean_encuestas, quarantine_encuestas)\n\n"
    "## 6. Conclusiones\n"
    "- Revisar áreas con baja satisfacción.\n"
    "- Analizar encuestas en cuarentena para posibles errores de ingreso.\n"
    "- Monitorizar evolución mensual para alertas de tendencias.\n"
)

(OUT / "reporte.md").write_text(report, encoding="utf-8")
print("OK · Generado:", OUT / "reporte.md")
print("OK · Parquet :", PARQUET_FILE if PARQUET_FILE.exists() else "sin datos")
print("OK · SQLite  :", DB)
