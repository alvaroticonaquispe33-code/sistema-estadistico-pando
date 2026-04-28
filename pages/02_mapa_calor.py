import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, MarkerCluster

# ----------------------------------
# Configuración página
# ----------------------------------
st.set_page_config(page_title="Mapa de Calor", layout="wide")
st.title("🔥 Sistema de Análisis Geoespacial - Pando")

# ----------------------------------
# Cargar datos
# ----------------------------------
filepath = "data/robos_limpio.csv"

try:
    df = pd.read_csv(filepath, encoding="utf-8", low_memory=False)
    
    # Blindaje de coordenadas (Puntos por comas)
    for col in ["LAT", "LON"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "."), errors="coerce")
    
    df = df.dropna(subset=["LAT", "LON"])
    
except Exception:
    st.error("⚠️ No se pudo leer robos_limpio.csv")
    st.stop()

# ----------------------------------
# LIMPIEZA INICIAL (GESTIÓN y MES)
# ----------------------------------
if "GESTION" in df.columns:
    df["GESTION"] = pd.to_numeric(df["GESTION"], errors="coerce")
    df = df[df["GESTION"].notna() & (df["GESTION"] >= 1900)]

if "MES" in df.columns:
    df["MES"] = df["MES"].astype(str).str.strip().str.upper()
    df = df[~df["MES"].isin(["-9999", "SIN_DATO", "NAN", "NONE"])]

# ----------------------------------
# 🎛️ SELECCIÓN DE VARIABLES PARA FILTRAR (Imagen 1)
# ----------------------------------
st.markdown("---")
st.subheader("⚙️ Configuración de Filtros")
columnas_disponibles = [c for c in df.columns if c not in ["LAT", "LON", "NUMERACION"]]
vars_para_filtrar = st.multiselect(
    "Seleccione qué variables desea usar para filtrar el mapa:",
    options=columnas_disponibles,
    default=["GESTION", "MES", "BARRIO", "TIPO_DE_HECHO"]
)

# Generar filtros dinámicos basados en la selección anterior
filtros_valores = {}
if vars_para_filtrar:
    cols = st.columns(len(vars_para_filtrar))
    for i, var in enumerate(vars_para_filtrar):
        with cols[i]:
            opciones = sorted(df[var].dropna().unique())
            filtros_valores[var] = st.multiselect(f"Filtrar {var}", opciones)

# ----------------------------------
# APLICAR FILTROS
# ----------------------------------
df_f = df.copy()
for var, valores in filtros_valores.items():
    if valores:
        df_f = df_f[df_f[var].isin(valores)]

if df_f.empty:
    st.warning("⚠️ No hay datos con los filtros seleccionados.")
    st.stop()

# ----------------------------------
# 1. CÁLCULO DE CENTRO
# ----------------------------------
center_lat = df_f["LAT"].mean()
center_lon = df_f["LON"].mean()

# ----------------------------------
# RENDERIZADO DE MAPAS (ADAPTADO A MÓVIL)
# ----------------------------------

# Inyectar CSS para que el mapa ocupe todo el ancho en celulares
st.markdown("""
    <style>
    [data-testid="stVerticalBlock"] > div:contains("Mapa") {
        width: 100%;
    }
    .stPlotlyChart { width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SECCIÓN: MAPA DE CALOR ---
st.markdown("---")
# En PC se ven lado a lado, en Móvil c2 baja debajo de c1
c1, c2 = st.columns([4, 1])

with c1:
    st.subheader("🔥 Mapa de Calor de Incidentes")
    m_calor = folium.Map(location=[center_lat, center_lon], zoom_start=13)
    heat_data = df_f[["LAT", "LON"]].values.tolist()
    HeatMap(heat_data, radius=18, blur=20, min_opacity=0.3).add_to(m_calor)
    
    # CAMBIO: width=None para que sea responsivo
    st_folium(m_calor, width=None, height=450, key="calor_movil", returned_objects=[])

with c2:
    st.subheader("📌 Leyenda")
    st.markdown("🔴 **Alta**\n\n🟡 **Media**\n\n🔵 **Baja**")

# --- SECCIÓN: MAPA DE PUNTOS ---
st.markdown("---")
# Usamos columnas para que la leyenda salga al lado en PC y debajo en Móvil
c3, c4 = st.columns([4, 1])

with c3:
    st.subheader("📍 Mapa de Puntos Exactos")
    m_puntos = folium.Map(location=[center_lat, center_lon], zoom_start=13)
    cluster = MarkerCluster(name="Incidentes").add_to(m_puntos)
    
    for _, row in df_f.head(300).iterrows():
        pop = f"<b>Barrio:</b> {row.get('BARRIO','S/D')}<br><b>Hecho:</b> {row.get('TIPO_DE_HECHO','S/D')}"
        folium.Marker(
            location=[row["LAT"], row["LON"]],
            popup=folium.Popup(pop, max_width=250),
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(cluster)
    
    # width=None permite que el mapa sea responsivo en celulares
    st_folium(m_puntos, width=None, height=450, key="puntos_movil", returned_objects=[])

with c4:
    # LEYENDA RESTAURADA PARA INTELIGENCIA POLICIAL
    st.subheader("📌 Leyenda")
    st.markdown("""
    🔵 **Punto Azul:** Ubicación exacta del hecho.  

    🟢🟡🔴 **Clusters:** Grupos de concentración de puntos (Haga clic para expandir).
    """)

st.markdown("---")
st.info(f"🔎 Registros visualizados: {len(df_f)}")

# ---------------------------------------------------------
# 🛡️ SECCIÓN DE INTELIGENCIA: RECOMENDACIÓN TÁCTICA
# ---------------------------------------------------------
st.markdown("---")
st.subheader("🛡️ Recomendación de Despliegue Operativo")

# Usamos df_f que es el DataFrame filtrado que ya tiene su Mapa de Calor
if not df_f.empty:
    col1, col2 = st.columns(2)

    with col1:
        try:
            # 1. Limpieza y extracción de hora
            # Buscamos la columna HORA (en mayúsculas por su limpieza previa)
            hora_col = "HORA" if "HORA" in df_f.columns else next((c for c in df_f.columns if "HORA" in c.upper()), None)
            
            if hora_col:
                hora_cruda = df_f[hora_col].astype(str).str.extract(r'(\d{1,2})').iloc[:, 0]
                if not hora_cruda.empty:
                    h_top = int(hora_cruda.value_counts().index[0])
                    # Conversión a formato 12h para el personal
                    periodo = "AM" if h_top < 12 else "PM"
                    hora_12 = h_top if 1 <= h_top <= 12 else (h_top - 12 if h_top > 12 else 12)
                    st.success(f"**Ventana de Riesgo Crítico:** Aproximadamente a las {hora_12}:00 {periodo}")
                else:
                    st.warning("🕒 Hora Crítica: No detectada")
            else:
                st.warning("🕒 Hora Crítica: Columna no encontrada")
        except:
            st.error("🕒 Error al calcular la hora táctica")

    with col2:
        # 2. Identificación del Día Crítico
        dia_col = "DIA" if "DIA" in df_f.columns else next((c for c in df_f.columns if "DIA" in c.upper()), None)
        
        if dia_col and not df_f.empty:
            dia_top = df_f[dia_col].value_counts().index[0]
            st.success(f"**Día de Alta Incidencia:** {str(dia_top).upper()}")
        else:
            st.warning("📅 Día Crítico: No detectado")

    # 3. Sugerencia dinámica según filtros
    lugar = "la zona seleccionada"
    if "BARRIO" in df_f.columns and len(df_f["BARRIO"].unique()) == 1:
        lugar = df_f["BARRIO"].unique()[0]

    st.warning(f"**Sugerencia del Sistema:** Incrementar patrullaje preventivo y paradas estacionarias en los sectores con mayor intensidad de calor (rojo) en **{lugar}**.")
else:
    st.info("Seleccione filtros para ver las recomendaciones tácticas.")
