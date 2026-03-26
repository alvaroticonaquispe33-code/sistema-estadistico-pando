import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

def entrenar_modelo():
    ruta = "data/robos_limpio.csv"

    print("\n📌 Cargando datos de robos_limpio.csv ...")
    df = pd.read_csv(ruta, encoding="utf-8")

    # Normalizar columnas
    df.columns = df.columns.str.upper().str.strip()

    # Columnas obligatorias según tu EXCEL real
    columnas = ["HORA", "MES", "LAT", "LON", "TIPO_DE_HECHO", "BARRIO"]

    for c in columnas:
        if c not in df.columns:
            raise ValueError(f"❌ FALTA LA COLUMNA REQUERIDA: {c}")

    # ----- PROCESAMIENTO -----

    # Hora → número entero HH
    df["HORA"] = df["HORA"].astype(str).str[:2]
    df["HORA"] = pd.to_numeric(df["HORA"], errors="coerce").fillna(0).astype(int)

    # Mes → convertir texto a número si aplica
    df["MES"] = df["MES"].astype(str).str.upper()
    meses = {
        "ENERO":1,"FEBRERO":2,"MARZO":3,"ABRIL":4,"MAYO":5,"JUNIO":6,
        "JULIO":7,"AGOSTO":8,"SEPTIEMBRE":9,"OCTUBRE":10,"NOVIEMBRE":11,"DICIEMBRE":12
    }
    df["MES"] = df["MES"].replace(meses)
    df["MES"] = pd.to_numeric(df["MES"], errors="coerce").fillna(0).astype(int)

    # Lat / Lon → número
    df["LAT"] = pd.to_numeric(df["LAT"], errors="coerce")
    df["LON"] = pd.to_numeric(df["LON"], errors="coerce")
    df = df.dropna(subset=["LAT", "LON"])

    # Codificar variables de texto
    enc_tipo = LabelEncoder()
    enc_barrio = LabelEncoder()

    df["TIPO_ENC"] = enc_tipo.fit_transform(df["TIPO_DE_HECHO"].astype(str))
    df["BARRIO_ENC"] = enc_barrio.fit_transform(df["BARRIO"].astype(str))

    # Variables para el modelo
    X = df[["HORA", "MES", "LAT", "LON", "TIPO_ENC"]]
    y = df["BARRIO_ENC"]

    # Entrenamiento
    print("📌 Entrenando modelo...")
    model = RandomForestClassifier(n_estimators=300, random_state=42)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test) * 100

    # Guardar modelo y encoders
    os.makedirs("model", exist_ok=True)
    pickle.dump(model, open("model/modelo_robos.pkl", "wb"))
    pickle.dump(enc_tipo, open("model/encoder_tipos.pkl", "wb"))
    pickle.dump(enc_barrio, open("model/encoder_barrios.pkl", "wb"))

    print(f"\n✅ Entrenamiento completado.")
    print(f"📊 Precisión del modelo: {accuracy:.2f}%")
    print("📦 Archivos guardados en /model/")
    print("   - modelo_robos.pkl")
    print("   - encoder_tipos.pkl")
    print("   - encoder_barrios.pkl")


if __name__ == "__main__":
    entrenar_modelo()
