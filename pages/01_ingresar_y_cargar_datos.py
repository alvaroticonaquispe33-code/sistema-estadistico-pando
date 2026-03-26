import streamlit as st
import pandas as pd
import os
from pathlib import Path
import unicodedata
import re

# Configuración inicial para móvil
st.set_page_config(page_title="Carga Policial Pando", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
# ------------------------------
# Configuración de Rutas
# ------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUT_CSV = DATA_DIR / "robos_limpio.csv"

# ------------------------------
# Funciones de Limpieza Avanzada
# ------------------------------

def limpiar_texto_policial(texto):
    """Limpieza profunda: Corrige BAR a BARRIO, CALE a CALLE y estandariza texto."""
    if pd.isna(texto): return "SIN DATO"
    
    # 1. Estandarizar: Mayúsculas, quitar acentos y símbolos
    s = str(texto).upper().strip()
    s = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII")
    s = re.sub(r'[^\w\s]', '', s)

    # 2. DICCIONARIO DE CORRECCIONES POR PREFIJO (Detecta el inicio de la palabra)
    # El símbolo ^ indica que la celda debe EMPEZAR con esa abreviatura
    correcciones = {
        r'^BAR\b': 'BARRIO',
        r'^BRR\b': 'BARRIO',
        r'^CALE\b': 'CALLE',
        r'^AV\b': 'AVENIDA',
        r'^AVDA\b': 'AVENIDA',
        r'^ZN\b': 'ZONA'
    }
    
    for error, correccion in correcciones.items():
        s = re.sub(error, correccion, s)
    
    # 3. Eliminar espacios dobles accidentales
    s = " ".join(s.split())
    
    return s

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza los nombres de las columnas del Excel."""
    new_cols = []
    for c in df.columns:
        s = str(c).strip().upper()
        s = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII")
        s = s.replace(" ", "_")
        new_cols.append(s)
    df.columns = new_cols
    return df

# ------------------------------
# INTERFAZ Y PROCESAMIENTO
# ------------------------------
st.set_page_config(page_title="Carga Policial Pando", layout="wide")
st.title("📥 Procesamiento de Datos - Policía Boliviana (Pando)")
st.markdown("### 🚨 Limpieza y Georreferenciación Automática")

uploaded = st.file_uploader("Subir Excel de Robos", type=["xlsx", "csv"])

if uploaded:
    try:
        # Cargar archivo
        df_subido = pd.read_excel(uploaded) if uploaded.name.endswith(".xlsx") else pd.read_csv(uploaded)
        df_subido = normalize_columns(df_subido)
        
        if st.button("🚀 Claridad y Limpieza: Procesar y Generar"):
            df_proc = df_subido.copy()
            
            # 1. LIMPIEZA DE TEXTO (BARRIO, CALLE, MAYÚSCULAS)
            columnas_texto = df_proc.select_dtypes(include=['object']).columns
            for col in columnas_texto:
                if col not in ["COORDENADAS", "COORDENADAS_UNICAS", "UBICACION"]:
                    df_proc[col] = df_proc[col].apply(limpiar_texto_policial)

            # 2. VALIDACIÓN ROBUSTA DE COORDENADAS (Evita Error LAT/LON)
            col_coords = next((c for c in ["COORDENADAS", "COORDENADAS_UNICAS", "UBICACION"] if c in df_proc.columns), None)
            
            if col_coords:
                def validar_y_separar(valor):
                    try:
                        texto = str(valor).strip()
                        if "," not in texto:
                            return None, None, "Falta la coma"
                        
                        partes = texto.split(",")
                        lat = float(partes[0].replace(",", ".").strip())
                        lon = float(partes[1].replace(",", ".").strip())
                        
                        # Validar rango Bolivia/Pando
                        if not (-25 < lat < -9 and -75 < lon < -55):
                            return lat, lon, "Fuera de rango (Bolivia)"
                            
                        return lat, lon, None
                    except:
                        return None, None, "Formato no numérico"

                # Ejecutar validación
                resultados = df_proc[col_coords].apply(validar_y_separar)
                df_proc["LAT"] = [r[0] for r in resultados]
                df_proc["LON"] = [r[1] for r in resultados]
                df_proc["ERROR_GPS"] = [r[2] for r in resultados]

                # Mostrar errores detectados en pantalla
                errores = df_proc[df_proc["ERROR_GPS"].notna()]
                if not errores.empty:
                    st.error(f"❌ Se detectaron {len(errores)} registros con error en '{col_coords}':")
                    st.dataframe(errores[[col_coords, "ERROR_GPS"]].head(10), width='stretch')
                    st.warning("⚠️ Estos registros se omitirán para no arruinar el mapa.")

                # Limpieza final de registros inválidos
                df_proc = df_proc.dropna(subset=["LAT", "LON"])
                
                if df_proc.empty:
                    st.error("❌ ERROR CRÍTICO: Ninguna coordenada es válida. Proceso detenido.")
                    st.stop()
            else:
                st.error("❌ No se encontró la columna de COORDENADAS.")
                st.stop()

            # 3. GUARDADO FINAL
            df_proc.to_csv(OUT_CSV, index=False, encoding="utf-8")
            
            st.success(f"✅ ¡Éxito! {len(df_proc)} registros listos.")
            
            # width='stretch' permite que el policía deslice la tabla con el dedo en su celular
            st.write("**Vista previa de datos (Deslice para ver más):**")
            st.dataframe(df_proc.head(), width='stretch')

    except Exception as e:
        st.error(f"❌ Error crítico: {e}")

# Estado del Sistema
if OUT_CSV.exists():
    st.markdown("---")
    df_count = pd.read_csv(OUT_CSV)
    st.info(f"📍 **Base de datos lista para el Mapa:** {len(df_count)} filas georreferenciadas en Cobija.")