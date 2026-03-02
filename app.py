import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(page_title="SISTEMA PLAN 200 - PANDO", layout="wide")

# --- COLORES INSTITUCIONALES EXTRAÍDOS ---
VERDE_FONDO_CLARO = "#D8F7C7" # image_12.png
VERDE_MEDIO = "#8BB644"       # image_13.png
VERDE_OSCURO = "#3E5728"      # image_14.png

# --- ESTILOS CSS PARA FONDO CLARO Y TEXTO OSCURO ---
st.markdown(f"""
    <style>
    /* 1. Fondo Degradado Claro */
    [data-testid="stAppViewContainer"] {{
        background: linear-gradient(180deg, {VERDE_FONDO_CLARO} 0%, #FFFFFF 100%);
    }}
    
    /* 2. Títulos Principales en Verde Muy Oscuro */
    [data-testid="stMarkdownContainer"] h1 {{
        color: {VERDE_OSCURO} !important;
        text-align: center;
    }}
    [data-testid="stMarkdownContainer"] h3 {{
        color: {VERDE_MEDIO} !important;
        text-align: center;
    }}

    /* 3. CORRECCIÓN DE LEGIBILIDAD: Todo el texto base a VERDE OSCURO */
    .stApp {{
        color: {VERDE_OSCURO} !important;
    }}
    
    /* 4. Métricas Superiores a VERDE OSCURO */
    [data-testid="stMetricValue"] {{
        color: {VERDE_OSCURO} !important;
        font-weight: bold;
    }}
    [data-testid="stMetricLabel"] p {{
        color: {VERDE_OSCURO} !important;
    }}
    
    /* 5. Títulos de Expansores a VERDE OSCURO */
    .streamlit-expanderHeader {{
        color: {VERDE_OSCURO} !important;
        background-color: rgba(62, 87, 40, 0.1);
    }}
    
    /* 6. Texto interno a VERDE OSCURO */
    [data-testid="stMarkdownContainer"] p, 
    [data-testid="stMarkdownContainer"] b,
    [data-testid="stMarkdownContainer"] strong {{
        color: {VERDE_OSCURO} !important;
    }}
    
    /* 7. Botones de Descargo */
    .stLinkButton button {{
        background-color: {VERDE_MEDIO} !important;
        color: white !important;
        border-radius: 10px;
        border: none;
    }}
    
    /* 8. Color del Sidebar */
    [data-testid="stSidebar"] {{
        background-color: #F0F2F6;
    }}
    [data-testid="stSidebar"] .stRadio label {{
        color: {VERDE_OSCURO} !important;
    }}

    /* 9. MEJORA GLOBAL: FORZAR TEXTO BLANCO EN FONDOS OSCUROS */
    div[style*="background-color: {VERDE_OSCURO}"], 
    div[style*="background-color: rgb(62, 87, 40)"] {{
        color: white !important;
    }}
    div[style*="background-color: {VERDE_OSCURO}"] * {{
        color: white !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- VINCULACIÓN CON GOOGLE SHEETS ---
SHEET_ID = "1k8nM6HQX9wXPtJ30GkCsWJdBBER1uSkAM1KzLydbNO0"

def cargar_desde_gsheets(nombre_hoja):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nombre_hoja}"
    return pd.read_csv(url)

st.markdown("<h1>COMANDO DEPARTAMENTAL DE POLICÍA PANDO</h1>", unsafe_allow_html=True)
st.markdown("<h3>DPTO. III - PLANEAMIENTO Y OPERACIONES</h3>", unsafe_allow_html=True)

# --- BOTÓN DE ACTUALIZACIÓN (MANTENIDO) ---
if st.sidebar.button("🔄 ACTUALIZAR DESDE LA NUBE"):
    st.cache_data.clear()
    st.rerun()

try:
    df_plan = cargar_desde_gsheets("Planificacion")
    df_res = cargar_desde_gsheets("Resultados")

    df_plan.columns = df_plan.columns.str.strip()
    df_res.columns = df_res.columns.str.strip()
    
    df_plan['ID ACT'] = df_plan['ID ACT'].astype(str).str.strip()
    df_res['ID ACT'] = df_res['ID ACT'].astype(str).str.strip()

    df_plan['META_TOTAL'] = pd.to_numeric(df_plan['META CANTIDAD'], errors='coerce').fillna(0)
    resumen_logros = df_res.groupby('ID ACT')['CANTIDAD'].sum().reset_index()

    df_final = pd.merge(df_plan, resumen_logros, on='ID ACT', how='left').fillna(0)
    df_final['PORCENTAJE'] = (df_final['CANTIDAD'] / df_final['META_TOTAL']) * 100
    df_final['PORCENTAJE'] = df_final['PORCENTAJE'].clip(upper=100).fillna(0)

    menu = st.sidebar.radio("MENÚ DE CONTROL:", ["📊 Resumen Estratégico", "🔍 Fiscalización de Oficiales"])

    if menu == "📊 Resumen Estratégico":
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("TAREAS EN GENERAL", "8")
        with m2: st.metric("ACCIONES TOTALES", len(df_final))
        with m3: st.metric("CUMPLIMIENTO TOTAL", f"{round(df_final['PORCENTAJE'].mean(), 1)}%")
        
        st.divider()
        
        avance_tareas = df_final.groupby('TAREA')['PORCENTAJE'].mean().reset_index()
        avance_tareas = avance_tareas.sort_values(by='PORCENTAJE', ascending=True)
        avance_tareas['LABEL'] = avance_tareas['PORCENTAJE'].apply(lambda x: f"{round(x, 1)}%")

        fig = px.bar(avance_tareas, x='PORCENTAJE', y='TAREA', orientation='h', 
                     title="AVANCE POR TAREA ESTRATÉGICA",
                     color='PORCENTAJE', 
                     color_continuous_scale=[[0, 'red'], [0.5, 'yellow'], [1, VERDE_OSCURO]],
                     text='LABEL')
        
        # --- AJUSTE DE COLOR EN BARRA LATERAL Y TEXTOS ---
        fig.update_traces(textposition='outside', textfont_color=VERDE_OSCURO, textfont_size=14)
        fig.update_layout(
            paper_bgcolor='white', 
            plot_bgcolor='rgba(0,0,0,0)',
            font_color=VERDE_OSCURO,
            title_font_color=VERDE_OSCURO,
            xaxis=dict(tickfont=dict(color=VERDE_OSCURO), title_font=dict(color=VERDE_OSCURO)),
            yaxis=dict(tickfont=dict(color=VERDE_OSCURO, size=11)),
            coloraxis_colorbar=dict(
                title="AVANCE %",
                title_font_color=VERDE_OSCURO,
                tickfont=dict(color=VERDE_OSCURO)
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)

    elif menu == "🔍 Fiscalización de Oficiales":
        tarea_sel = st.selectbox("Seleccione Tarea para Fiscalizar:", df_final['TAREA'].unique())
        df_t = df_final[df_final['TAREA'] == tarea_sel]

        col1, col2, col3 = st.columns(3)
        with col1: st.metric("ACCIONES EN TAREA", len(df_t))
        with col2: st.metric("OFICIALES DESIGNADOS", df_t['JEFE U OFICIAL DESIGNADO'].nunique())
        with col3: st.metric("CUMPLIMIENTO DE TAREA", f"{round(df_t['PORCENTAJE'].mean(), 1)}%")
        
        st.divider()

        for _, fila in df_t.iterrows():
            with st.expander(f"📋 {fila['ID ACT']} | {fila['ACTIVIDAD'][:60]}..."):
                c1, c2 = st.columns([1.5, 1])
                with c1:
                    st.write(f"**Indicador:** {fila.get('INDICADOR DE RESULTADO', 'N/A')}")
                    st.write(f"**Unidad:** {fila.get('UNIDAD O DIRECCION POLICIAL', 'N/A')}")
                    st.write(f"**Temporalidad:** {fila.get('TEMPORALIDAD', 'N/A')}")
                    
                    id_act = fila['ID ACT']
                    docs = df_res[df_res['ID ACT'] == id_act]
                    
                    if 'LINK DE EVIDENCIA' in docs.columns:
                        links = docs['LINK DE EVIDENCIA'].dropna()
                        if not links.empty:
                            with st.popover("📂 VER DESCARGOS (PDF)"):
                                for i, link in enumerate(links):
                                    if "http" in str(link):
                                        st.link_button(f"📄 Documento #{i+1}", str(link), use_container_width=True)
                        else:
                            st.caption("No hay links registrados.")

                with c2:
                    oficial = fila.get('JEFE U OFICIAL DESIGNADO', 'S/A')
                    # Aplicamos fondo institucional y forzamos color blanco
                    st.markdown(f"""
                        <div style='background-color:{VERDE_OSCURO}; color:white !important; font-weight:bold; padding:8px; border-radius:5px;'>
                            👮 Oficial: {oficial}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    p = round(fila['PORCENTAJE'], 1)
                    st.write(f"**Progreso:** {p}%")
                    st.progress(p/100)
                    st.write(f"**Logro:** {int(fila['CANTIDAD'])} de {int(fila['META_TOTAL'])}")

except Exception as e:
    st.error(f"Error detectado: {e}")