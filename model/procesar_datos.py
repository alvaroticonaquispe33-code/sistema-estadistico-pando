# procesar_datos.py
import pandas as pd
import os

def limpiar_y_guardar():
    ruta = "data/historial_robos.xlsx"
    if not os.path.exists(ruta):
        raise FileNotFoundError(ruta)

    df = pd.read_excel(ruta)
    print("Leyendo", ruta)

    # Normalizar columnas
    df.columns = df.columns.str.strip().str.upper().str.replace(" ", "_")

    # Normalizar lat/lon
    for c in ["LAT", "LATITUD", "LATITUDE"]:
        if c in df.columns:
            df = df.rename(columns={c: "LAT"})
    for c in ["LON", "LONG", "LONGITUD", "LONGITUDE"]:
        if c in df.columns:
            df = df.rename(columns={c: "LON"})

    # Parsear fecha
    if "FECHA" in df.columns:
        df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce", dayfirst=True)
        df["AÑO"] = df["FECHA"].dt.year

    # Forzar numericos en lat/lon
    if "LAT" in df.columns:
        df["LAT"] = pd.to_numeric(df["LAT"], errors="coerce")
    if "LON" in df.columns:
        df["LON"] = pd.to_numeric(df["LON"], errors="coerce")

    # Llenar nulos simples o marcar
    for col in df.columns:
        if df[col].isna().any():
            if df[col].dtype == "float64" or df[col].dtype == "int64":
                df[col] = df[col].fillna(-9999)
            else:
                df[col] = df[col].fillna("SIN_DATO")

    # Eliminar filas sin coordenadas válidas
    before = len(df)
    df = df.dropna(subset=["LAT", "LON"])
    after = len(df)
    print(f"Filas antes: {before}, después de limpiar coords: {after}")

    # Guardar CSV limpio
    out_csv = "data/robos_limpio.csv"
    df.to_csv(out_csv, index=False)
    print("Guardado:", out_csv)
    return out_csv

if __name__ == "__main__":
    try:
        limpiar_y_guardar()
    except Exception as e:
        print("Error en limpieza:", e)
