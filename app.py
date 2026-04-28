import streamlit as st
import base64

# Configuración de página
st.set_page_config(
    page_title="Sistema de Inteligencia - Pando",
    page_icon="🚔",
    layout="wide"
)

# Función para convertir imagen local a base64 (necesario para el fondo CSS)
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Intentar cargar la imagen de fondo
try:
    bin_str = get_base64_image("scripts/banner_bicentenario.jpg")
    background_style = f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url("data:image/jpg;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* Logo de Estadística arriba a la derecha */
    .logo-estadistica {{
        position: absolute;
        top: 10px;
        right: 10px;
        width: 100px;
        z-index: 999;
    }}

    .slogan-final {{
        font-family: 'Georgia', serif;
        font-size: 28px;
        font-weight: bold;
        color: #D4AC0D;
        text-align: center;
        margin-top: 100px;
        text-shadow: 2px 2px 4px #000000;
    }}
    
    h1, h3, p {{
        color: white !important;
        text-shadow: 2px 2px 4px #000000;
    }}
    </style>
    """
    st.markdown(background_style, unsafe_allow_html=True)
except Exception as e:
    st.error("⚠️ No se pudo cargar el fondo. Verifique que 'scripts/banner_bicentenario.jpg' exista.")

# 2. LOGO DE ESTADÍSTICA DINÁMICO
try:
    logo_base64 = get_base64_image("scripts/logo_estadistica.png")
    st.markdown(f'<img src="data:image/png;base64,{logo_base64}" class="logo-estadistica">', unsafe_allow_html=True)
except:
    pass

# 3. CONTENIDO CENTRAL
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; font-size: 50px;'>SISTEMA DE MAPA DE CALOR Y GEOREFERENCIACION</h1>", unsafe_allow_html=True)

# Mensaje de instrucción debajo del título
st.markdown("<p style='text-align: center; font-size: 20px; color: #D4AC0D !important;'>⚠️ Seleccione una sección en el menú lateral izquierdo para comenzar.</p>", unsafe_allow_html=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# 4. OBJETIVO Y DINOSAURIO
col_obj, col_space, col_dino = st.columns([0.6, 0.1, 0.3])

with col_obj:
    st.markdown("### 🎯 Objetivo")
    st.markdown("""
    <p style='font-size: 18px; text-align: justify;'>
    Optimizar y facilitar el trabajo estadístico de las unidades y direcciones del 
    Comando Departamental de Policía Pando, mediante la implementación de un sistema 
    de georreferenciación y mapa de calor, que permita el registro, análisis y 
    visualización de información operativa para la adecuada toma de decisiones y 
    el fortalecimiento de la seguridad ciudadana.
    </p>
    """, unsafe_allow_html=True)

with col_dino:
    st.image("scripts/dinosaurio_policia.png", width=220)

# 5. SLOGAN INSTITUCIONAL
st.markdown('<p class="slogan-final">“200 AÑOS DE HISTORIA, VOCACION Y SERVICIO A LA SOCIEDAD”</p>', unsafe_allow_html=True)