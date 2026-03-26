from train_model import entrenar_modelo

# Entrenar y cargar el modelo en RAM
modelo = entrenar_modelo()

# Lista de columnas que el modelo espera
features = ["AÑO", "MES", "PROVINCIA", "MUNICIPIO", "BARRIO", "LAT", "LON"]

def predecir(df):
    df_model = df[features].copy()

    # Codificar categorías igual que en entrenamiento
    for col in ["PROVINCIA", "MUNICIPIO", "BARRIO"]:
        df_model[col] = df_model[col].astype("category").cat.codes

    pred = modelo.predict(df_model)
    df["prediccion"] = pred
    return df
