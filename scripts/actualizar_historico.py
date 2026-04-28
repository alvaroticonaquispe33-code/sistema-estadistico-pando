# scripts/actualizar_historico.py
import pandas as pd
import os
import sys

# Config
INPUT_FILE = "DIPROV.xlsx"              # cambia si tu Excel tiene otro nombre
OUT_DIR = "data"
OUT_FILE = os.path.join(OUT_DIR, "base_historica.csv")

if not os.path.exists(INPUT_FILE):
    print("ERROR: no encuentro el archivo de entrada:", INPUT_FILE)
    sys.exit(1)

# Crear carpeta data si no existe
os.makedirs(OUT_DIR, exist_ok=True)

# 1) Cargar Excel
print("Cargando:", INPUT_FILE)
df = pd.read_excel(INPUT_FILE)

# 2) Normalizar nombres de columnas esperadas (ajusta si tu Excel usa otros nombres)
rename_map = {}
for c in df.columns:
    low = c.strip().lower()
    if low in ("numeracion","num","id"):
        rename_map[c] = "NUMERACION"
    elif "fecha" in low:
        rename_map[c] = "FECHA"
    elif "hora" in low:
        rename_map[c] = "HORA"
    elif low in ("año","anio","año","year"):
        rename_map[c] = "AÑO"
    elif "mes" in low:
        rename_map[c] = "MES"
    elif "provincia" in low:
        rename_map[c] = "PROVINCIA"
    elif "municipio" in low:
        rename_map[c] = "MUNICIPIO"
    elif "barrio" in low:
        rename_map[c] = "BARRIO"
    elif "lat" in low:
        rename_map[c] = "LAT"
    elif "lon" in low or "long" in low:
        rename_map[c] = "LON"
    elif "tipo" in low and "hecho" in low:
        rename_map[c] = "TIPO_HECHO"
    elif "observ" in low:
        rename_map[c] = "OBSERVACIONES"

df = df.rename(columns=rename_map)

# 3) Convertir FECHA/HORA a tipos
if "FECHA" in df.columns:
    df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce", dayfirst=True)
if "HORA" in df.columns:
    # Intentamos normalizar HORA si viene como número/texto
    df["HORA"] = df["HORA"].astype(str).str.strip()

# 4) Textos en mayúsculas: BARRIO, PROVINCIA, MUNICIPIO, TIPO_HECHO
for txt_col in ["BARRIO","PROVINCIA","MUNICIPIO","TIPO_HECHO","OBSERVACIONES"]:
    if txt_col in df.columns:
        df[txt_col] = df[txt_col].astype(str).str.strip().str.upper()

# 5) Forzar LAT/LON numéricos y eliminar filas sin coords
if "LAT" in df.columns and "LON" in df.columns:
    df["LAT"] = pd.to_numeric(df["LAT"], errors="coerce")
    df["LON"] = pd.to_numeric(df["LON"], errors="coerce")
    before = len(df)
    df = df.dropna(subset=["LAT","LON"])
    after = len(df)
    print(f"Filas totales: {before}, después de quitar sin coords: {after}")
else:
    print("ADVERTENCIA: No se detectaron columnas LAT y LON. Se guardará sin filtrado de coords.")

# 6) Crear ID si no existe
if "NUMERACION" not in df.columns:
    df.insert(0, "NUMERACION", range(1, len(df)+1))

# 7) Guardar CSV limpio (reemplaza completamente)
df.to_csv(OUT_FILE, index=False)
print("Historico limpio guardado en:", OUT_FILE)
