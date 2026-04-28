import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ----------------------------------
# 📱 Configuración Página Responsive
# ----------------------------------
st.set_page_config(
    page_title="Dashboard Estadístico Pando",
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Estilos CSS para mejorar visualización en celular
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 2rem;
    }
    .stDeployButton {
        display:none;
    }
    @media (max-width: 768px) {
        .stPlotlyChart {
            height: 300px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Panel Estadístico Dinámico - Pando")

# ----------------------------------
# 📥 Cargar datos (Sin guardar nada)
# ----------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
FILEPATH = DATA_DIR / "robos_limpio.csv"

@st.cache_data
def cargar_datos_limpios(path):
    if not path.exists(): return None
    df = pd.read_csv(path, encoding="utf-8")
    return df

df = cargar_datos_limpios(FILEPATH)
# Definimos df_f inmediatamente después de cargar los datos
df_f = df.copy()
if df is None or df.empty:
    st.error("⚠️ No se detectaron datos limpios. Procese un Excel en la pestaña de Carga.")
    st.stop()

# ----------------------------------
# 🃏 CARTAS DE MÉTRICAS (Blindadas y Actualizadas)
# ----------------------------------
st.markdown("---")
m1, m2, m3, m4 = st.columns([1, 1, 1, 1])

# Aseguramos que los nombres de las columnas no tengan espacios invisibles
df_f.columns = [c.strip().upper() for c in df_f.columns]

with m1:
    if "BARRIO" in df_f.columns and not df_f.empty:
        conteo_barrios = df_f["BARRIO"].value_counts()
        st.metric(label="🚨 Barrio Crítico", value=conteo_barrios.index[0])

with m2:
    if "TIPO_DE_HECHO" in df_f.columns and not df_f.empty:
        conteo_hechos = df_f["TIPO_DE_HECHO"].value_counts()
        st.metric(label="⚠️ Delito Frecuente", value=conteo_hechos.index[0])

with m3:
    # Verificamos si existe 'DIA' o 'DIAS' por si acaso
    col_dia = next((c for c in df_f.columns if "DIA" in c), None)
    if col_dia and not df_f.empty:
        conteo_dia = df_f[col_dia].value_counts()
        if not conteo_dia.empty:
            st.metric(label="📅 Día Crítico", value=str(conteo_dia.index[0]).upper())
    else:
        st.metric(label="📅 Día Crítico", value="NO DETECTADO")

with m4:
    if "HORA" in df_f.columns and not df_f.empty:
        # 1. Convertimos a texto y extraemos solo los primeros dos números (la hora)
        # Esto limpia formatos como 21:00:00 o 210000
        hora_cruda = df_f['HORA'].astype(str).str.extract(r'(\d{1,2})').iloc[:, 0]
        
        # 2. Obtenemos la hora más frecuente
        if not hora_cruda.empty:
            h_top = int(hora_cruda.value_counts().index[0])
            
            # 3. Lógica para convertir a formato AM/PM
            periodo = "AM" if h_top < 12 else "PM"
            hora_12 = h_top if 1 <= h_top <= 12 else (h_top - 12 if h_top > 12 else 12)
            
            # 4. Mostramos el resultado final: HRS 19 PM
            st.metric(label="🕒 Hora Crítica", value=f"HRS {hora_12} {periodo}")
    else:
        st.metric(label="🕒 Hora Crítica", value="S/D")
# --- NUEVA UBICACIÓN DE FILTROS (Encima de la configuración) ---
st.markdown("---")
st.subheader("🔍 Filtrar Datos para el Gráfico")
f1, f2 = st.columns(2)

# Reiniciamos df_f para que el filtro de arriba afecte al gráfico de abajo
with f1:
    if "GESTION" in df.columns:
        gestiones = sorted(df["GESTION"].unique().tolist(), reverse=True)
        sel_gestion = st.multiselect("Filtrar por Gestión:", gestiones, default=gestiones)
        if sel_gestion:
            df_f = df_f[df_f["GESTION"].isin(sel_gestion)]

with f2:
    if "MES" in df.columns:
        meses = sorted(df["MES"].unique().tolist())
        sel_mes = st.multiselect("Filtrar por Mes:", meses, default=meses)
        if sel_mes:
            df_f = df_f[df_f["MES"].isin(sel_mes)]    
# ----------------------------------
# ⚙️ CONFIGURACIÓN DEL GRÁFICO (Flexible)
# ----------------------------------
st.markdown("---")
st.subheader("⚙️ Configuración del Análisis")

cols_graficables = [c for c in df_f.columns if c not in ["LAT", "LON", "NUMERACION", "FECHA", "HORA", "COORDENADAS_UNICAS", "LUGAR_ESPECIFICO_DEL_HECHO", "OBSERVACIONES"]]

c_config1, c_config2 = st.columns([2, 1])

with c_config1:
    var_analisis = st.selectbox(
        "📊 Seleccione la variable principal para analizar:",
        options=cols_graficables,
        index=cols_graficables.index("TIPO_DE_HECHO") if "TIPO_DE_HECHO" in cols_graficables else 0
    )

with c_config2:
    tipo_grafico = st.radio(
        "📈 Tipo de Visualización:",
        options=["Barras (Comparar)", "Líneas (Tendencia)", "Pastel (Porcentaje)"],
        horizontal=True
    )

# PREPARACIÓN DE DATOS CORRECTA (Se eliminó la línea con error)
df_chart = df_f[var_analisis].value_counts().reset_index()
df_chart.columns = [var_analisis, "CANTIDAD_CASOS"]

# ----------------------------------
# 📈 RENDERIZADO DEL GRÁFICO (Mejorado)
# ----------------------------------
st.markdown("---")

if not df_chart.empty:
    if tipo_grafico == "Barras (Comparar)":
        # Escala de colores Rojo-Amarillo-Verde (Semáforo Policial)
        fig = px.bar(
            df_chart, 
            x=var_analisis, 
            y="CANTIDAD_CASOS", 
            text="CANTIDAD_CASOS",
            color="CANTIDAD_CASOS",
            color_continuous_scale=["#2ECC71", "#F1C40F", "#E74C3C"], # Verde, Amarillo, Rojo
            labels={var_analisis: var_analisis.replace("_", " "), "CANTIDAD_CASOS": "Cantidad"}
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        # Esto elimina los decimales (.5) y comas de los años
        fig.update_xaxes(type='category')
    elif tipo_grafico == "Líneas (Tendencia)":
        if var_analisis == "MES":
            orden_meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
            df_chart[var_analisis] = pd.Categorical(df_chart[var_analisis], categories=orden_meses, ordered=True)
            df_chart = df_chart.sort_values(var_analisis)

        fig = px.line(
            df_chart, x=var_analisis, y="CANTIDAD_CASOS", 
            markers=True, text="CANTIDAD_CASOS" # Añade el valor sobre el punto
        )
        fig.update_traces(textposition="top center")

    elif tipo_grafico == "Pastel (Porcentaje)":
        # Formato solicitado: (Cantidad; Porcentaje) y sin nombres adentro
        fig = px.pie(
            df_chart, 
            values="CANTIDAD_CASOS", 
            names=var_analisis, 
            hole=0.4
        )
        fig.update_traces(
            textinfo='value+percent', 
            texttemplate='%{value}; %{percent}', # Formato (15; 2%)
            textposition='inside'
        )

    # Ajustes finales de diseño
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.8, xanchor="center", x=0.5),
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True, key="grafico_final")

else:
    st.warning("No hay suficientes datos para generar el gráfico.")
st.markdown("---")
st.caption("🚨 Sistema de Inteligencia Policial - Pando.")