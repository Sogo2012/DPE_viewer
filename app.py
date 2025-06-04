import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
# import io # No se usa directamente
import datetime
import base64
import os
import requests # Para la función de GeoJSON
import zipfile # Para la función de GeoJSON
import io      # Para la función de GeoJSON

# --- DEFINICIÓN DE COLORES Y CSS AL INICIO ---
COLOR_AZUL_ECO = "#173D4A"
COLOR_VERDE_ECO = "#66913E"
COLOR_GRIS_ECO = "#414549"
COLOR_TEXTO_TITULO_PRINCIPAL_CSS = COLOR_AZUL_ECO
COLOR_TEXTO_SUBTITULO_SECCION_CSS = COLOR_VERDE_ECO
COLOR_TEXTO_SUB_SUBTITULO_CSS = COLOR_GRIS_ECO
COLOR_TEXTO_CUERPO_CSS = "#333333"
COLOR_TEXTO_SUTIL_CSS = "#7f8c8d"
COLOR_TEXTO_BLANCO_CSS = "#FFFFFF"
# ESTE ES EL BLOQUE CORRECTO PARA REEMPLAZAR LA ASIGNACIÓN DE CSS_STYLES
CSS_STYLES = f"""
<style>
    /* === ESTILOS PARA PESTAÑAS (st.tabs) === */

    /* Contenedor de la lista de pestañas */
    div[data-baseweb="tab-list"] {{
        gap: 8px !important; /* Espacio entre pestañas reducido */
        border-bottom: 3px solid transparent !important; 
        padding-bottom: 0px !important; 
    }}

    /* Pestaña individual (botón) */
    div[data-baseweb="tab-list"] button[data-baseweb="tab"] {{
        height: auto !important; 
        min-height: 48px; /* Altura para acomodar dos líneas */
        white-space: normal !important; /* Permitir múltiples líneas */
        overflow-wrap: anywhere; /* Romper palabras largas si es necesario */
        hyphens: manual; /* Desactivar guiones automáticos */
        text-align: center !important; /* Centrar texto */
        display: flex !important; /* Para centrado vertical/horizontal */
        align-items: center !important;
        justify-content: center !important;
        
        border-radius: 8px 8px 0px 0px !important; 
        padding: 6px 6px !important; /* Padding ajustado (vertical 6px, horizontal 8px) */
        font-weight: 500 !important;
        font-size: 10px !important; /* Tamaño de fuente reducido */
        line-height: 1.25 !important; /* Altura de línea ajustada */
        
        border: none !important; /* Quitar todos los bordes por defecto */
        border-bottom: 3px solid transparent !important; /* Borde inferior transparente por defecto */
        margin-bottom: -3px !important; /* Compensar borde del contenedor */
        
        transition: background-color 0.2s ease, color 0.2s ease, border-bottom-color 0.2s ease !important;
    }}

    /* Texto DENTRO de CUALQUIER pestaña (párrafo) */
    div[data-baseweb="tab-list"] button[data-baseweb="tab"] div[data-testid="stMarkdownContainer"] p {{
        color: {COLOR_TEXTO_BLANCO_CSS} !important; 
        margin-bottom: 0 !important; 
        line-height: inherit !important; 
        font-size: inherit !important; 
        font-weight: inherit !important; 
    }}
    
    /* Pestaña individual (NO ACTIVA) */
    div[data-baseweb="tab-list"] button[data-baseweb="tab"][aria-selected="false"] {{
        background-color: {COLOR_GRIS_ECO} !important; 
    }}

    /* Pestaña individual (ACTIVA) */
    div[data-baseweb="tab-list"] button[data-baseweb="tab"][aria-selected="true"] {{
        background-color: {COLOR_AZUL_ECO} !important; 
        font-weight: 700 !important; 
        border-bottom-color: {COLOR_VERDE_ECO} !important; 
    }}

    /* Ajuste para el contenedor interno del tab-list */
    div[data-baseweb="tab-list"] > div {{
        border-bottom: none !important;
    }}
    /* === FIN ESTILOS PARA PESTAÑAS === */

    /* Estilos generales */
    h1 {{ color: {COLOR_TEXTO_TITULO_PRINCIPAL_CSS}; padding-bottom: 0.5rem; border-bottom: 3px solid {COLOR_AZUL_ECO}; }}
    h2 {{ color: {COLOR_TEXTO_SUBTITULO_SECCION_CSS}; border-bottom: 2px solid {COLOR_VERDE_ECO}; padding-bottom: 0.3rem; margin-top: 2rem; }}
    h3 {{ color: {COLOR_TEXTO_SUB_SUBTITULO_CSS}; margin-top: 1.5rem; }}
    p, div, span, li, .stMarkdown {{ color: {COLOR_TEXTO_CUERPO_CSS}; line-height: 1.6; }}
    .stCaption {{ color: {COLOR_TEXTO_SUTIL_CSS}; }}
    hr {{ margin-top: 0.5rem; margin-bottom: 1rem; border: 0; border-top: 1px solid #D5D8DC; }}
</style>
"""
# --- FIN DEFINICIÓN DE COLORES Y CSS ---


# URL del GeoJSON de GADM para Costa Rica (Provincias)
URL_GEOJSON_GADM_PROVINCIAS_CR_ZIP = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_CRI_1.json.zip"
GEOJSON_FILENAME = "gadm41_CRI_1.json"

@st.cache_data(ttl=60*60*24)
def load_geojson_costa_rica():
    # ... (código de la función sin cambios)
    try:
        response = requests.get(URL_GEOJSON_GADM_PROVINCIAS_CR_ZIP, stream=True, timeout=30)
        response.raise_for_status()
        zip_in_memory = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_in_memory, 'r') as zip_ref:
            if GEOJSON_FILENAME in zip_ref.namelist():
                with zip_ref.open(GEOJSON_FILENAME) as geojson_file:
                    geojson_data = json.load(geojson_file)
                return geojson_data
            else:
                st.error(f"Archivo '{GEOJSON_FILENAME}' no encontrado dentro del ZIP descargado.")
                return None
    except Exception as e:
        st.error(f"Error procesando GeoJSON: {e}")
        return None

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
APP_TITLE = "Visualizador Avanzado de Informes DPE - ECO Consultores"
LOGO_FILENAME = "Logo_ECO.png"
LOGO_DIRECTORY = "assets"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(SCRIPT_DIR, LOGO_DIRECTORY, LOGO_FILENAME)
logo_exists_at_path = os.path.exists(LOGO_PATH)

def get_image_as_base64(path):
    # ... (código de la función sin cambios)
    if not os.path.exists(path): return None
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except Exception: return None

logo_base64 = get_image_as_base64(LOGO_PATH)
page_icon_img_to_set = "📊"
if logo_exists_at_path:
    try: page_icon_img_to_set = Image.open(LOGO_PATH)
    except Exception: pass

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=page_icon_img_to_set,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'mailto:soporte@ecoconsultores.com',
        'Report a bug': "mailto:soporte@ecoconsultores.com",
        'About': f"### {APP_TITLE}\nVersión 1.2\n\nDesarrollado con Streamlit."
    }
)

# APLICAR EL CSS DESPUÉS DE st.set_page_config
st.markdown(CSS_STYLES, unsafe_allow_html=True)


# --- 3. ESTADO DE LA APLICACIÓN ---
# ... (tu código de inicialización de session_state se mantiene igual) ...
if 'json_data' not in st.session_state:
    st.session_state.json_data = None
if 'nombre_cliente' not in st.session_state:
    st.session_state.nombre_cliente = "Cliente"
if 'error_carga' not in st.session_state:
    st.session_state.error_carga = None
if 'show_json_data' not in st.session_state:
    st.session_state.show_json_data = False

# --- 4. BARRA LATERAL ---
# ... (tu código de la barra lateral se mantiene igual) ...
with st.sidebar:
    if logo_base64:
        st.markdown(
            f'<div style="display: flex; justify-content: center; padding-bottom:10px;"><img src="data:image/png;base64,{logo_base64}" alt="Logo ECO Consultores" style="max-width: 80%; height: auto;"></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(f"<h2 style='color:{COLOR_AZUL_ECO}; text-align:center;'>ECO Consultores</h2>", unsafe_allow_html=True)

    st.markdown("---")
    st.header("Cargar Informe DPE")
    uploaded_file = st.file_uploader(
        "Seleccione el archivo JSON:",
        type=["json"],
        key="dpe_json_uploader",
        help="Arrastre y suelte un archivo JSON o haga clic para seleccionar."
    )

    if uploaded_file is not None:
        with st.spinner("Procesando archivo JSON..."):
            try:
                string_data = uploaded_file.getvalue().decode("utf-8")
                if string_data.startswith('\ufeff'):
                    string_data = string_data.lstrip('\ufeff')
                st.session_state.json_data = json.loads(string_data)
                st.session_state.error_carga = None
                if st.session_state.json_data and "metadatos_informe" in st.session_state.json_data:
                    nombre_cliente_json = st.session_state.json_data["metadatos_informe"].get("cliente_nombre")
                    st.session_state.nombre_cliente = nombre_cliente_json if nombre_cliente_json else "Cliente (Nombre no en JSON)"
                else:
                    st.session_state.nombre_cliente = "Cliente (Metadatos no en JSON)"
                st.success(f"✓ Archivo '{uploaded_file.name}' cargado para {st.session_state.nombre_cliente}.")
            except json.JSONDecodeError as jde:
                st.session_state.error_carga = f"Error de Decodificación: El archivo no es un JSON válido. Detalle: {jde}"
                st.session_state.json_data = None
                st.error(st.session_state.error_carga) 
            except Exception as e:
                st.session_state.error_carga = f"Error Crítico al procesar: {str(e)}."
                st.session_state.json_data = None
                st.error(st.session_state.error_carga) 

    if st.session_state.get('json_data', None): # Usar .get()
        st.markdown("---")
        if st.button("🧹 Limpiar Datos y Reiniciar"):
            keys_to_delete = list(st.session_state.keys())
            for key in keys_to_delete:
                del st.session_state[key]
            # Re-inicializar estados básicos AHORA SÍ ANTES DEL RERUN
            st.session_state.json_data = None
            st.session_state.nombre_cliente = "Cliente"
            st.session_state.error_carga = None
            st.session_state.show_json_data = False
            st.rerun()
        st.session_state.show_json_data = st.toggle("Mostrar datos JSON crudos", value=st.session_state.get('show_json_data', False))


# --- DEFINICIONES DE FUNCIONES DE RENDERIZADO ---
# ... (TODAS TUS FUNCIONES render_portada, render_glosario, render_resumen_ejecutivo, 
#      render_introduccion_contexto, render_analisis_externo (con la corrección de gráficos CFIA),
#      render_diagnostico_interno, render_sintesis_foda, render_formulacion_estrategica,
#      render_hoja_ruta, render_implementacion, render_conclusiones (con la corrección de duplicación)
#      VAN AQUÍ SIN CAMBIOS INTERNOS, solo asegúrate que las variables de color que usen
#      estén definidas globalmente o sean pasadas como argumentos si es necesario)
#      Por brevedad, no las repito aquí, pero deben estar en tu archivo.
#      Solo he puesto la función render_analisis_externo como ejemplo de que va aquí.
# -------------------------------------------------------------------------------------
def render_portada(data):
    st.markdown(f"<div style='padding: 20px; text-align:center;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color: {COLOR_TEXTO_TITULO_PRINCIPAL_CSS}; font-size: 2.5em; margin-top: 50px;'>{data.get('titulo_principal_texto', 'Título Portada')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 1.8em; color: {COLOR_TEXTO_TITULO_PRINCIPAL_CSS};'>{data.get('preparado_para_texto', 'Preparado para:')} <b style='color:{COLOR_VERDE_ECO}'>{data.get('nombre_cliente_texto', st.session_state.nombre_cliente)}</b></p>", unsafe_allow_html=True)
    
    metadatos_informe_local = {}
    if st.session_state.json_data and "metadatos_informe" in st.session_state.json_data:
         metadatos_informe_local = st.session_state.json_data["metadatos_informe"]
    
    st.markdown(f"<p style='font-size: 1.1em; color: {COLOR_GRIS_ECO}; margin-bottom: 100px;'>{data.get('fecha_diagnostico_texto', metadatos_informe_local.get('fecha_diagnostico', 'N/A'))}</p>", unsafe_allow_html=True)

    if logo_exists_at_path:
        try:
            st.image(LOGO_PATH, width=250)
        except Exception as e:
            st.markdown(f"<p style='font-size: 0.8em; color: {COLOR_TEXTO_SUTIL_CSS};'>(Error al mostrar logo de portada con st.image: {e}. Ruta: {LOGO_PATH})</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='font-size: 0.8em; color: {COLOR_TEXTO_SUTIL_CSS};'>(Logo de portada no encontrado en '{LOGO_PATH}')</p>", unsafe_allow_html=True)

    st.markdown(f"<p style='font-size: 0.9em; color: {COLOR_GRIS_ECO}; margin-top: 100px;'>{data.get('footer_linea1_texto', 'Un informe de ECO Consultores')}</p>", unsafe_allow_html=True)
    version_dpe_info = metadatos_informe_local.get("version_dpe", "N/A")
    default_footer_line2_text = f'Herramienta DPE {version_dpe_info}'
    footer_line2_content = data.get('footer_linea2_texto', default_footer_line2_text)
    st.markdown(f"<p style='font-size: 0.9em; color: {COLOR_GRIS_ECO};'>{footer_line2_content}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def render_glosario(data):
    st.header(data.get('titulo_seccion_texto', 'X. Glosario de Términos')) 
    st.markdown("---")
    if not data.get("lista_terminos_data"):
        st.info("No hay términos en el glosario para mostrar.")
        return
    for item in data.get("lista_terminos_data", []):
        term = item.get('termino_texto', 'N/A')
        definition = item.get('definicion_texto', 'N/A')
        with st.container():
            st.markdown(f"**{term}**")
            st.markdown(definition)
            st.markdown("---")

def render_resumen_ejecutivo(data_re):
    st.header(data_re.get('titulo_seccion_texto', "I. Resumen Ejecutivo Gerencial"))
    sec_proposito = data_re.get("proposito_alcance", {})
    st.subheader(sec_proposito.get('subtitulo_texto', '1.1. Propósito y Alcance'))
    st.write(sec_proposito.get('parrafo_texto', 'N/A'))
    sec_madurez_global = data_re.get("madurez_global", {})
    st.subheader(sec_madurez_global.get('subtitulo_texto', '1.2. Nivel de Madurez Global'))
    st.write(sec_madurez_global.get('parrafo_texto', 'N/A'))
    radar_data_list = sec_madurez_global.get("grafico_radar_data", [])
    if radar_data_list and isinstance(radar_data_list, list) and len(radar_data_list) >= 3:
        labels = [item.get('label') for item in radar_data_list if item.get('label') is not None]
        values_str = [item.get('value') for item in radar_data_list if item.get('value') is not None]
        values = []
        for v_str in values_str:
            try: values.append(float(v_str))
            except (ValueError, TypeError): values.append(0.0) 
        if labels and values and len(labels) == len(values):
            fig_radar = go.Figure()
            r_fill, g_fill, b_fill = tuple(int(COLOR_VERDE_ECO.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            fill_color_rgba = f'rgba({r_fill}, {g_fill}, {b_fill}, 0.6)'
            fig_radar.add_trace(go.Scatterpolar(
                r=values + ([values[0]] if values else []), 
                theta=labels + ([labels[0]] if labels else []), 
                fill='toself', fillcolor=fill_color_rgba,
                line_color=COLOR_AZUL_ECO
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], ticksuffix='%', showline=True,
                                    showticklabels=True, ticks='outside', dtick=20,
                                    gridcolor=COLOR_GRIS_ECO, linecolor=COLOR_GRIS_ECO,
                                    tickfont=dict(size=9, color=COLOR_GRIS_ECO)),
                    angularaxis=dict(showline=False, ticks='outside', direction="clockwise",
                                     tickfont=dict(size=10, color=COLOR_TEXTO_CUERPO_CSS))
                ),
                title=dict(text=sec_madurez_global.get("grafico_radar_titulo_sugerido", "Nivel de Madurez por Área (%)"),
                           x=0.5, font=dict(size=16, color=COLOR_TEXTO_TITULO_PRINCIPAL_CSS)),
                showlegend=False, height=450, margin=dict(l=50, r=50, t=80, b=50),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=COLOR_TEXTO_CUERPO_CSS, size=11)
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            st.caption(sec_madurez_global.get("grafico_radar_caption_texto", 
                                              sec_madurez_global.get("grafico_radar_titulo_sugerido", "")))
        else:
            st.caption("Datos para gráfico radar incompletos o con formato incorrecto.")
    else:
        st.caption("Datos para gráfico radar no disponibles o insuficientes.")
    sub_secciones_resumen = ["hallazgos_area", "foda_interno", "foda_externo", 
                             "lineamientos_estrategicos", "conclusion_resumen_ejecutivo"]
    for sub_key in sub_secciones_resumen:
        sub_data = data_re.get(sub_key, {})
        if sub_data: 
            st.subheader(sub_data.get('subtitulo_texto', sub_key.replace("_", " ").title())) 
            if "parrafo_texto" in sub_data: st.write(sub_data.get('parrafo_texto'))
            if "parrafo_intro_texto" in sub_data: st.write(sub_data.get('parrafo_intro_texto'))
            if "lista_textos_hallazgos" in sub_data:
                for item in sub_data.get("lista_textos_hallazgos", []): st.markdown(f"• {item}")
            if "fortalezas_lista_textos" in sub_data:
                st.markdown(f"**{sub_data.get('fortalezas_titulo_texto','Fortalezas:')}**")
                for item in sub_data.get("fortalezas_lista_textos", []): st.markdown(f"• {item}")
            if "debilidades_lista_textos" in sub_data:
                st.markdown(f"**{sub_data.get('debilidades_titulo_texto','Debilidades:')}**")
                for item in sub_data.get("debilidades_lista_textos", []): st.markdown(f"• {item}")
            if "oportunidades_lista_textos" in sub_data:
                st.markdown(f"**{sub_data.get('oportunidades_titulo_texto','Oportunidades:')}**")
                for item in sub_data.get("oportunidades_lista_textos", []): st.markdown(f"• {item}")
            if "amenazas_lista_textos" in sub_data:
                st.markdown(f"**{sub_data.get('amenazas_titulo_texto','Amenazas:')}**")
                for item in sub_data.get("amenazas_lista_textos", []): st.markdown(f"• {item}")
            if "lista_lineamientos_textos" in sub_data:
                 for item in sub_data.get("lista_lineamientos_textos", []): st.markdown(f"• {item}")
            st.markdown("---")

def render_introduccion_contexto(data):
    st.header(data.get('titulo_seccion_texto', "II. Introducción y Contexto del Diagnóstico"))
    seccion_presentacion = data.get("presentacion_cliente", {})
    st.subheader(seccion_presentacion.get('subtitulo_texto', "A. Presentación"))
    for key, val in seccion_presentacion.items():
        if key not in ['subtitulo_texto', 'titulo_seccion_texto'] and isinstance(val, str): 
            st.markdown(f"**{key.replace('_texto', '').replace('_', ' ').title()}:** {val}")
    st.markdown("---")
    seccion_objetivos = data.get("objetivos_dpe", {})
    st.subheader(seccion_objetivos.get('subtitulo_texto', "B. Objetivos DPE"))
    st.write(seccion_objetivos.get('parrafo_intro_texto', ""))
    for item in seccion_objetivos.get('lista_objetivos_textos', []): st.markdown(f"• {item}")
    st.markdown("---")
    seccion_alcance = data.get("alcance_metodologia", {})
    st.subheader(seccion_alcance.get('subtitulo_texto', "C. Alcance y Metodología"))
    st.write(seccion_alcance.get('parrafo_areas_texto', ""))
    st.markdown(f"**{seccion_alcance.get('proceso_recoleccion_titulo_texto','Proceso de Recolección y Marco de Evaluación:')}**")
    for item in seccion_alcance.get('lista_metodologia_textos', []): st.markdown(f"• {item}")
    st.caption(seccion_alcance.get('parrafo_limitaciones_texto', ""))

def render_analisis_externo(data): # VERSIÓN CON GRÁFICOS CFIA ADICIONALES
    st.header(data.get('titulo_seccion_texto', "III. Análisis del Entorno Externo"))
    
    # --- A. Análisis del Macroentorno (BCCR) ---
    sec_macro = data.get("macroentorno", {})
    st.subheader(sec_macro.get('subtitulo_texto', "A. Análisis del Macroentorno"))
    st.write(sec_macro.get('parrafo_intro_indicadores_texto', ""))

    if "grafico_bccr_data" in sec_macro and sec_macro["grafico_bccr_data"] and isinstance(sec_macro["grafico_bccr_data"], list) and len(sec_macro["grafico_bccr_data"]) > 0 and not (len(sec_macro["grafico_bccr_data"])==1 and sec_macro["grafico_bccr_data"][0].get("Error")):
        df_bccr = pd.DataFrame(sec_macro["grafico_bccr_data"])
        if not df_bccr.empty and 'Fecha' in df_bccr.columns:
            try:
                df_bccr['Fecha'] = pd.to_datetime(df_bccr['Fecha'])
                tbp_col = 'Tasa_Basica_Pasiva'
                tc_col = 'Tipo_Cambio_Venta_Referencia'
                fig_bccr = go.Figure()
                tbp_data_exists = False
                tc_data_exists = False

                if tbp_col in df_bccr.columns:
                    df_bccr[tbp_col] = pd.to_numeric(df_bccr[tbp_col], errors='coerce')
                    if not df_bccr[tbp_col].isnull().all():
                        fig_bccr.add_trace(go.Scatter(x=df_bccr['Fecha'], y=df_bccr[tbp_col], name='Tasa Básica Pasiva (%)', yaxis='y1', line=dict(color=COLOR_AZUL_ECO)))
                        tbp_data_exists = True
                
                if tc_col in df_bccr.columns:
                    df_bccr[tc_col] = pd.to_numeric(df_bccr[tc_col], errors='coerce')
                    if not df_bccr[tc_col].isnull().all():
                        fig_bccr.add_trace(go.Scatter(x=df_bccr['Fecha'], y=df_bccr[tc_col], name='Tipo de Cambio Venta (CRC)', yaxis='y2', line=dict(color=COLOR_VERDE_ECO)))
                        tc_data_exists = True
                
                if tbp_data_exists or tc_data_exists:
                    fig_bccr.update_layout(
                        title_text=sec_macro.get("grafico_bccr_titulo_sugerido", "Indicadores Económicos Clave (BCCR)"), title_x=0.5,
                        xaxis_title='Fecha',
                        yaxis=dict(title=dict(text='Tasa Básica Pasiva (%)', font=dict(color=COLOR_AZUL_ECO)), 
                                   tickfont=dict(color=COLOR_AZUL_ECO), side='left', showgrid=False,
                                   visible=tbp_data_exists), 
                        yaxis2=dict(title=dict(text='Tipo de Cambio Venta (CRC)', font=dict(color=COLOR_VERDE_ECO)), 
                                    tickfont=dict(color=COLOR_VERDE_ECO), overlaying='y', side='right', 
                                    showgrid=tc_data_exists, gridcolor='rgba(0,0,0,0.05)',
                                    visible=tc_data_exists), 
                        legend_title_text='Indicadores', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        font_color=COLOR_TEXTO_CUERPO_CSS
                    )
                    st.plotly_chart(fig_bccr, use_container_width=True)
                    st.caption(sec_macro.get("grafico_bccr_caption_texto", sec_macro.get("grafico_bccr_titulo_sugerido","")))
                else:
                    st.info("No hay datos válidos para Tasa Básica Pasiva o Tipo de Cambio en el archivo JSON.")
            except Exception as e:
                st.error(f"Error al procesar datos para gráfico BCCR: {e}")
        else:
            st.info("Datos para gráfico BCCR no disponibles o en formato incorrecto (falta columna 'Fecha' o datos vacíos).")
    else:
        st.info("No se encontraron datos para el gráfico BCCR en 'macroentorno' o los datos son inválidos.")
    st.markdown("---")

    # --- B. Análisis del Sector/Industria (CFIA) ---
    sec_cfia = data.get("sector_industria_cfia", {})
    st.subheader(sec_cfia.get('subtitulo_texto', "B. Análisis del Sector/Industria (Construcción Costa Rica)"))
    st.write(sec_cfia.get('parrafo_intro_texto', ""))

    # 1. Gráfico de Tendencia M² CFIA
    tend_data = sec_cfia.get("grafico_tendencia_m2_data", {})
    # Condición más robusta para verificar si hay datos para el gráfico de tendencia
    if tend_data and (tend_data.get("historico") or tend_data.get("actual_real") or tend_data.get("actual_proyeccion")):
        try:
            df_hist = pd.DataFrame(tend_data.get("historico", []))
            df_proy = pd.DataFrame(tend_data.get("actual_proyeccion", []))
            df_real = pd.DataFrame(tend_data.get("actual_real", []))
            
            fig_tend = go.Figure()

            if not df_hist.empty and 'Mes' in df_hist.columns:
                for col in df_hist.columns:
                    if col != 'Mes': 
                        df_hist[col] = pd.to_numeric(df_hist[col], errors='coerce')
                        fig_tend.add_trace(go.Scatter(x=df_hist['Mes'], y=df_hist[col], mode='lines+markers', name=f'Hist. {col}', line=dict(width=1.5), marker=dict(size=4)))
            
            last_real_month_name = None
            last_real_value = None
            if not df_real.empty and 'Mes' in df_real.columns and 'Valor_Actual' in df_real.columns:
                df_real['Valor_Actual'] = pd.to_numeric(df_real['Valor_Actual'], errors='coerce')
                df_real_plot = df_real.dropna(subset=['Valor_Actual'])
                if not df_real_plot.empty:
                    fig_tend.add_trace(go.Scatter(x=df_real_plot['Mes'], y=df_real_plot['Valor_Actual'], mode='lines+markers', name='Actual Real', line=dict(color='black', width=2.5), marker=dict(size=6)))
                    last_real_month_name = df_real_plot['Mes'].iloc[-1]
                    last_real_value = df_real_plot['Valor_Actual'].iloc[-1]

            if not df_proy.empty and 'Mes' in df_proy.columns and 'Valor_Proyeccion' in df_proy.columns:
                df_proy['Valor_Proyeccion'] = pd.to_numeric(df_proy['Valor_Proyeccion'], errors='coerce')
                df_proy_for_plot = df_proy.dropna(subset=['Valor_Proyeccion']).copy()

                if last_real_month_name and last_real_value is not None:
                    df_to_prepend = pd.DataFrame([{'Mes': last_real_month_name, 'Valor_Proyeccion': last_real_value}])
                    if not df_proy_for_plot.empty and df_proy_for_plot['Mes'].iloc[0] == last_real_month_name:
                         df_proy_for_plot = df_proy_for_plot[df_proy_for_plot['Mes'] != last_real_month_name]
                    df_proy_for_plot = pd.concat([df_to_prepend, df_proy_for_plot], ignore_index=True)
                    df_proy_for_plot.drop_duplicates(subset=['Mes'], keep='first', inplace=True)

                if not df_proy_for_plot.empty:
                     fig_tend.add_trace(go.Scatter(x=df_proy_for_plot['Mes'], y=df_proy_for_plot['Valor_Proyeccion'], mode='lines+markers', name='Proyección', line=dict(dash='dashdot', color='red', width=2.5), marker=dict(symbol='x', size=6)))
            
            fig_tend.update_layout(
                title_text=sec_cfia.get("grafico_tendencia_m2_titulo_sugerido", "Tendencia M² Construidos (CFIA)"), title_x=0.5,
                xaxis_title='Mes', yaxis_title='M² Construidos',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color=COLOR_TEXTO_CUERPO_CSS,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_tend, use_container_width=True)
            st.caption(sec_cfia.get("grafico_tendencia_m2_caption_texto", sec_cfia.get("grafico_tendencia_m2_titulo_sugerido","")))
        except Exception as e:
            st.error(f"Error al generar gráfico de tendencia CFIA: {e}")
    else:
        st.info("Datos para gráfico de tendencia M2 (CFIA) no disponibles o incompletos.")

    # --- INICIO NUEVOS GRÁFICOS CFIA ---
    
    # 2. Gráfico de Variación Provincial CFIA
    var_prov_data = sec_cfia.get("grafico_variacion_provincial_data", [])
    if var_prov_data and isinstance(var_prov_data, list) and not (len(var_prov_data) == 1 and var_prov_data[0].get("Provincia") == "N/A"):
        df_var_prov = pd.DataFrame(var_prov_data)
        if 'Provincia' in df_var_prov.columns and 'Variacion_%' in df_var_prov.columns:
            df_var_prov['Variacion_%'] = pd.to_numeric(df_var_prov['Variacion_%'], errors='coerce')
            df_var_prov.dropna(subset=['Variacion_%'], inplace=True)
            df_var_prov = df_var_prov.sort_values(by='Variacion_%', ascending=False)
            
            fig_var_prov = px.bar(df_var_prov, x='Provincia', y='Variacion_%',
                                  title=sec_cfia.get("grafico_variacion_provincial_titulo_sugerido", "Variación M² por Provincia"),
                                  labels={'Variacion_%': 'Variación Porcentual (%)', 'Provincia':'Provincia'},
                                  color='Variacion_%',
                                  color_continuous_scale=[(0, "red"), (0.45, "lightgrey"),(0.5, "lightgrey"), (0.55, "lightgrey"), (1, "green")],
                                  color_continuous_midpoint=0)
            fig_var_prov.update_layout(
                title_x=0.5,
                yaxis_ticksuffix="%",
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                font_color=COLOR_TEXTO_CUERPO_CSS,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_var_prov, use_container_width=True)
            st.caption(sec_cfia.get("grafico_variacion_provincial_caption_texto", "Fuente: CFIA"))
        else:
            st.info("Datos para gráfico de variación provincial CFIA incompletos (faltan columnas 'Provincia' o 'Variacion_%').")
    else:
        st.info("No hay datos disponibles para el gráfico de variación provincial CFIA.")

    # 3. Mapa Coroplético M² Provincial CFIA
    mapa_data = sec_cfia.get("mapa_m2_provincial_data", [])
    if mapa_data and isinstance(mapa_data, list) and not (len(mapa_data) == 1 and mapa_data[0].get("Provincia_Compatible") == "N/A"):
        geojson_costa_rica = load_geojson_costa_rica() 

        if geojson_costa_rica:
            try:
                df_mapa = pd.DataFrame(mapa_data)
                for feature in geojson_costa_rica['features']:
                    if 'properties' in feature and 'NAME_1' in feature['properties']:
                         nombre_prov_original = feature['properties']['NAME_1']
                         nombre_prov_normalizado = nombre_prov_original.lower().replace('san jose', 'sanjosé').replace('san josé', 'sanjosé').replace('limon', 'limón').title()
                         feature['properties']['Provincia_Compatible_Geo'] = nombre_prov_normalizado 
                    else:
                        if 'properties' not in feature: feature['properties'] = {}
                        feature['properties']['Provincia_Compatible_Geo'] = "ErrorNombreGeo"

                fig_mapa = px.choropleth_mapbox(df_mapa, geojson=geojson_costa_rica, 
                                         locations='Provincia_Compatible', 
                                         featureidkey="properties.Provincia_Compatible_Geo", 
                                         color='m2_construidos',
                                         color_continuous_scale="Viridis", 
                                         mapbox_style="carto-positron", 
                                         zoom=6, center = {"lat": 9.7489, "lon": -83.7534}, 
                                         opacity=0.7,
                                         labels={'m2_construidos':'M² Construidos'},
                                         title=sec_cfia.get("mapa_m2_provincial_titulo_sugerido", "M² Acumulados por Provincia")
                                        )
                fig_mapa.update_layout(
                    title_x=0.5, 
                    margin={"r":0,"t":40,"l":0,"b":0}, 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color=COLOR_TEXTO_CUERPO_CSS
                )
                st.plotly_chart(fig_mapa, use_container_width=True)
                st.caption(sec_cfia.get("mapa_m2_provincial_caption_texto", "Fuente: CFIA"))
            except Exception as e_mapa:
                st.error(f"Error al generar mapa coroplético: {e_mapa}")
                if geojson_costa_rica and 'features' in geojson_costa_rica and geojson_costa_rica['features']:
                    st.json(geojson_costa_rica['features'][0]['properties']) 
        else:
            st.warning("No se pudo cargar el GeoJSON para el mapa.")
    else:
        st.info("No hay datos disponibles para el mapa coroplético de M² por provincia.")

    # 4. Gráficos de Desglose por Tipo de Obra CFIA
    desglose_obra_data = sec_cfia.get("graficos_desglose_obra_data", {})
    captions_desglose = sec_cfia.get("captions_desglose_obra", {})
    if desglose_obra_data:
        st.subheader(sec_cfia.get("desglose_tipo_obra_subtitulo_texto", "Desglose M² por Tipo de Obra (CFIA)"))
        
        col1_obra, col2_obra = st.columns(2)
        columns_map = {0: col1_obra, 1: col2_obra}
        col_idx = 0

        for tipo_obra, datos_obra_lista in desglose_obra_data.items():
            if datos_obra_lista and isinstance(datos_obra_lista, list):
                df_obra = pd.DataFrame(datos_obra_lista)
                if not df_obra.empty and 'Mes' in df_obra.columns:
                    meses = df_obra['Mes'].tolist()
                    subobras_cols = [col for col in df_obra.columns if col != 'Mes']
                    
                    fig_obra = go.Figure()
                    for sub_col in subobras_cols:
                        # Solo añadir la traza si la columna de subobra existe y tiene datos
                        if sub_col in df_obra.columns and df_obra[sub_col].sum() > 0:
                             fig_obra.add_trace(go.Bar(name=sub_col, x=meses, y=df_obra[sub_col]))
                    
                    if not fig_obra.data: # Si no se añadió ninguna traza
                        st.info(f"No hay datos de M² significativos para graficar para Tipo de Obra: {tipo_obra}")
                        continue

                    fig_obra.update_layout(
                        barmode='stack',
                        title=captions_desglose.get(tipo_obra, f"M² Mensuales: {tipo_obra}"),
                        title_x=0.5,
                        xaxis_title='Mes',
                        yaxis_title='M² Construidos',
                        legend_title_text='Sub-Tipo de Obra',
                        paper_bgcolor='rgba(0,0,0,0)', 
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color=COLOR_TEXTO_CUERPO_CSS
                    )
                    
                    current_column = columns_map[col_idx % 2]
                    with current_column:
                        st.plotly_chart(fig_obra, use_container_width=True)
                        st.caption(captions_desglose.get(tipo_obra, f"Fuente: CFIA - {tipo_obra}"))
                    col_idx += 1
                else:
                    with columns_map[col_idx % 2]: # Poner el mensaje en la columna correspondiente
                        st.info(f"No hay datos válidos para graficar el tipo de obra: {tipo_obra}")
                    col_idx += 1
            else:
                 with columns_map[col_idx % 2]:
                    st.info(f"Datos para tipo de obra '{tipo_obra}' no disponibles o en formato incorrecto.")
                 col_idx += 1
        if sec_cfia.get("nota_graficos_adicionales_texto"):
            st.caption(sec_cfia.get("nota_graficos_adicionales_texto"))
    else:
        st.info("No hay datos disponibles para el desglose por tipo de obra CFIA.")
    # --- FIN NUEVO CÓDIGO ---

    # --- C. Análisis de la Competencia (tu código actual) ---
    sec_comp = data.get("analisis_competencia", {})
    st.subheader(sec_comp.get('subtitulo_texto', "C. Análisis de la Competencia"))
    st.write(sec_comp.get('parrafo_intro_texto', ""))
    for i, comp in enumerate(sec_comp.get('lista_competidores_data', [])):
        nombre_competidor = comp.get('nombre_y_url_texto', '').split('(')[0].strip()
        if not nombre_competidor: nombre_competidor = f"Competidor {comp.get('id_competidor_display_texto', i+1)}"
        with st.expander(f"{comp.get('id_competidor_display_texto', f'Competidor {i+1}')}: {nombre_competidor}", expanded=i==0): 
            st.markdown(f"**URL:** {comp.get('nombre_y_url_texto', 'N/A')}")
            st.markdown(f"**Giro Principal:** {comp.get('giro_principal_inferido_texto', 'N/A')}")
            st.markdown(f"**Productos/Servicios Clave:** {comp.get('productos_servicios_clave_texto', 'N/A')}")
            st.markdown(f"**Propuesta de Valor:** {comp.get('propuesta_valor_observada_texto', 'N/A')}")
            st.markdown(f"**{comp.get('fortalezas_clave_titulo_texto', 'Fortalezas Clave:')}**")
            for f_item in comp.get('fortalezas_clave_lista_textos', []): st.markdown(f"• {f_item}")
    st.caption(sec_comp.get('nota_adicionales_texto', ""))
    st.markdown("---")

    # --- D. Huella Digital y Ecosistema Online (tu código actual) ---
    sec_huella = data.get("huella_digital_ecosistema", {})
    st.subheader(sec_huella.get('subtitulo_texto', "D. Huella Digital y Ecosistema Online"))
    st.markdown(f"**{sec_huella.get('cliente_titulo_texto', 'Huella Digital del Cliente')}**")
    st.write(sec_huella.get('cliente_evaluacion_sitio_texto', ""))
    st.caption(sec_huella.get('cliente_palabras_clave_sugeridas_texto', ""))
    st.markdown(f"**{sec_huella.get('ecosistema_titulo_texto', 'Ecosistema Digital del Sector y Tendencias')}**")
    st.write(sec_huella.get('ecosistema_google_trends_intro_texto', ""))
    for item in sec_huella.get('ecosistema_google_trends_lista_textos', []): st.markdown(f"• {item}")
    st.markdown("---")

    # --- E. Síntesis de Oportunidades y Amenazas Externas (tu código actual) ---
    sec_sint_ext = data.get("sintesis_oportunidades_amenazas_externas", {})
    st.subheader(sec_sint_ext.get('subtitulo_texto', "E. Síntesis de Oportunidades y Amenazas Externas"))
    st.markdown(f"**{sec_sint_ext.get('oportunidades_titulo_texto', 'Principales Oportunidades Externas:')}**")
    for item in sec_sint_ext.get('oportunidades_lista_textos', []): st.markdown(f"• {item}")
    st.markdown(f"**{sec_sint_ext.get('amenazas_titulo_texto', 'Principales Amenazas Externas:')}**")
    for item in sec_sint_ext.get('amenazas_lista_textos', []): st.markdown(f"• {item}")

def render_diagnostico_interno(data):
    st.header(data.get('titulo_seccion_texto', "IV. Diagnóstico Interno: Evaluación de Capacidades y Madurez Estratégica"))
    sec_mad_glob = data.get("madurez_global_organizacion", {})
    st.subheader(sec_mad_glob.get('subtitulo_texto', "A. Nivel de Madurez Global de la Organización"))
    st.write(sec_mad_glob.get('parrafo_puntuacion_texto', ""))
    st.write(sec_mad_glob.get('parrafo_explicacion_texto', ""))
    st.markdown("---")
    sec_eval_areas = data.get("evaluacion_detallada_areas", {})
    st.subheader(sec_eval_areas.get('subtitulo_texto', "B. Evaluación Detallada por Áreas Estratégicas de Madurez"))
    for area_data in sec_eval_areas.get('lista_areas_evaluacion_data', []):
        area_titulo_display = area_data.get('titulo_area_display_pdf_style', "Área no especificada")
        with st.expander(area_titulo_display, expanded=True): 
            st.write(area_data.get('nivel_madurez_display_texto', ""))
            graf_data = area_data.get('grafico_barra_madurez_data', {})
            if graf_data.get('label') and graf_data.get('value') is not None:
                try:
                    value = float(graf_data['value'])
                    df_bar = pd.DataFrame([{'Área': graf_data['label'], 'Madurez (%)': value}])
                    fig_bar = px.bar(df_bar, x='Madurez (%)', y='Área', orientation='h', range_x=[0,100],
                                     color_discrete_sequence=[COLOR_VERDE_ECO])
                    fig_bar.update_layout(height=150, margin=dict(l=10, r=10, t=30, b=10),
                                          title_text=area_data.get('grafico_barra_madurez_caption_texto', f"Madurez: {graf_data['label']}"), 
                                          title_x=0.5,
                                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                          font_color=COLOR_TEXTO_CUERPO_CSS)
                    st.plotly_chart(fig_bar, use_container_width=True)
                except ValueError:
                    st.warning(f"Valor no numérico para gráfico de barra en '{area_titulo_display}': {graf_data['value']}")
            st.markdown(f"**{area_data.get('interpretacion_negocio_titulo_texto', 'Interpretación para el Negocio:')}**")
            st.write(area_data.get('interpretacion_negocio_parrafo_texto', ""))
            st.markdown(f"**{area_data.get('fortalezas_clave_titulo_texto', 'Fortalezas Clave Identificadas (Nivel >= 4):')}**")
            fortalezas_list = area_data.get('fortalezas_clave_lista_data', [])
            if fortalezas_list:
                for f_item in fortalezas_list:
                    st.markdown(f"• {f_item.get('criterio_texto', '')} {f_item.get('nivel_texto', '')}")
            else:
                st.write(area_data.get('fortalezas_clave_placeholder_texto', "No se identificaron fortalezas con nivel 4 o 5 en esta área."))
            st.markdown(f"**{area_data.get('oportunidades_mejora_titulo_texto', 'Oportunidades de Mejora Críticas (Nivel <= 2):')}**")
            st.write(area_data.get('oportunidades_mejora_resumen_texto', "")) 
    st.markdown("---")
    sec_sint_int = data.get("sintesis_foda_interna", {})
    st.subheader(sec_sint_int.get('subtitulo_texto', "C. Síntesis de Fortalezas y Debilidades Internas Clave"))
    st.markdown(f"**{sec_sint_int.get('fortalezas_titulo_texto', 'Principales Fortalezas Internas Consolidadas:')}**")
    for item in sec_sint_int.get('fortalezas_lista_textos', []): st.markdown(f"• {item}")
    st.markdown(f"**{sec_sint_int.get('debilidades_titulo_texto', 'Principales Debilidades Internas Críticas:')}**")
    for item in sec_sint_int.get('debilidades_lista_textos', []): st.markdown(f"• {item}")

def render_sintesis_foda(data):
    st.header(data.get('titulo_seccion_texto', "V. Síntesis Estratégica: Matriz FODA y Desafíos Estratégicos"))
    texto_sesion_trabajo = "Este análisis requiere una sesión de trabajo colaborativa. Se recomienda realizarla con los líderes de proceso y Eco Consultor para identificar la estrategia a seguir y definir los próximos pasos."
    sec_matriz = data.get("matriz_foda_integrada", {})
    st.subheader(sec_matriz.get('subtitulo_texto', "A. Presentación de la Matriz FODA Integrada"))
    st.write(sec_matriz.get('parrafo_intro_texto', ""))
    foda_data = sec_matriz.get('tabla_foda_data', {})
    if foda_data:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"#### {sec_matriz.get('titulos_cuadrantes_foda_textos', {}).get('fortalezas', 'FORTALEZAS')}")
            for item in foda_data.get('fortalezas_lista_textos', ["(No listadas)"]): st.markdown(f"• {item}")
            st.markdown("---") 
            st.markdown(f"#### {sec_matriz.get('titulos_cuadrantes_foda_textos', {}).get('oportunidades', 'OPORTUNIDADES')}")
            for item in foda_data.get('oportunidades_lista_textos', ["(No listadas)"]): st.markdown(f"• {item}")
        with col2:
            st.markdown(f"#### {sec_matriz.get('titulos_cuadrantes_foda_textos', {}).get('debilidades', 'DEBILIDADES')}")
            for item in foda_data.get('debilidades_lista_textos', ["(No listadas)"]): st.markdown(f"• {item}")
            st.markdown("---") 
            st.markdown(f"#### {sec_matriz.get('titulos_cuadrantes_foda_textos', {}).get('amenazas', 'AMENAZAS')}")
            for item in foda_data.get('amenazas_lista_textos', ["(No listadas)"]): st.markdown(f"• {item}")
    else:
        st.info("Datos para la matriz FODA no disponibles.")
    st.markdown("---")
    sec_tows = data.get("analisis_cruzado_tows", {})
    st.subheader(sec_tows.get('subtitulo_texto', "B. Análisis Cruzado (TOWS) e Implicaciones Estratégicas"))
    placeholder_tows = sec_tows.get('parrafo_placeholder_texto', texto_sesion_trabajo)
    if "(Placeholder:" in placeholder_tows or not sec_tows.get('parrafo_texto_analisis_FO') : 
         st.info(placeholder_tows) 
    else: 
        st.write(sec_tows.get('parrafo_intro_texto', "A continuación se presenta el análisis cruzado:"))
        st.markdown(f"**Estrategias FO (Fortalezas-Oportunidades):** {sec_tows.get('parrafo_texto_analisis_FO', 'N/A')}")
        st.markdown(f"**Estrategias DO (Debilidades-Oportunidades):** {sec_tows.get('parrafo_texto_analisis_DO', 'N/A')}")
        st.markdown(f"**Estrategias FA (Fortalezas-Amenazas):** {sec_tows.get('parrafo_texto_analisis_FA', 'N/A')}")
        st.markdown(f"**Estrategias DA (Debilidades-Amenazas):** {sec_tows.get('parrafo_texto_analisis_DA', 'N/A')}")
    st.markdown("---")
    sec_desafios = data.get("desafios_estrategicos_clave", {})
    st.subheader(sec_desafios.get('subtitulo_texto', "C. Identificación de los Desafíos Estratégicos Clave"))
    placeholder_desafios = sec_desafios.get('parrafo_placeholder_texto', texto_sesion_trabajo)
    if "(Placeholder:" in placeholder_desafios or not sec_desafios.get('lista_desafios_textos'):
        st.info(placeholder_desafios)
    else:
        st.write(sec_desafios.get('parrafo_intro_texto', "Los desafíos estratégicos clave identificados son:"))
        for desafio in sec_desafios.get('lista_desafios_textos', []):
            st.markdown(f"• {desafio}")

def render_formulacion_estrategica(data):
    st.header(data.get('titulo_seccion_texto', "VI. Formulación Estratégica: Definiendo el Rumbo"))
    sec_identidad = data.get("identidad_estrategica", {})
    st.subheader(sec_identidad.get('subtitulo_texto', "A. Revisión/Definición de la Identidad Estratégica"))
    st.write(sec_identidad.get('parrafo_introductorio_texto', 
             "La definición o revisión de la Misión, Visión y Valores Corporativos es un ejercicio estratégico clave. Se recomienda realizar un taller interno para (re)definir estos elementos fundamentales."))
    st.markdown(f"**Misión Sugerida:** {sec_identidad.get('mision_sugerida_texto', 'N/A')}")
    st.markdown(f"**Visión Sugerida:** {sec_identidad.get('vision_sugerida_texto', 'N/A')}")
    st.markdown(f"**{sec_identidad.get('titulo_valores_sugeridos_texto', 'Valores Corporativos Sugeridos:')}**")
    for val in sec_identidad.get('lista_valores_sugeridos_textos', ["(No definidos)"]): st.markdown(f"• {val}")
    st.markdown("---")
    sec_obj = data.get("objetivos_estrategicos_prioritarios", {})
    st.subheader(sec_obj.get('subtitulo_texto', "B. Objetivos Estratégicos Prioritarios (Próximos 2-3 años)"))
    st.write(sec_obj.get('parrafo_intro_texto', 
             "Los siguientes objetivos estratégicos han sido identificados como prioritarios:"))
    for i, obj_data in enumerate(sec_obj.get('lista_objetivos_data', [])):
        obj_titulo = obj_data.get('titulo_objetivo_texto', f'Objetivo Estratégico {i+1}')
        st.markdown(f"**{obj_data.get('id_display_pdf_style', f'OE{i+1}')}: {obj_titulo}**")
        st.caption(obj_data.get('descripcion_detallada_texto', ''))
        st.markdown(f"_{obj_data.get('kpis_metas_titulo_texto', 'Métricas Clave de Éxito (KPIs) y Metas:')}_ {obj_data.get('kpis_metas_contenido_texto', 'Se definirán en la fase de planificación detallada.')}")
        st.markdown(f"_{obj_data.get('alineacion_desafios_titulo_texto', 'Alineación con Desafíos Clave:')}_ {obj_data.get('alineacion_desafios_contenido_texto', 'Se alineará con los desafíos estratégicos una vez definidos.')}")
        if i < len(sec_obj.get('lista_objetivos_data', [])) - 1: st.markdown("---") 
    st.markdown("---")
    sec_prop_valor = data.get("propuesta_valor_diferenciada", {})
    st.subheader(sec_prop_valor.get('subtitulo_texto', "C. Propuesta de Valor Diferenciada"))
    st.write(sec_prop_valor.get('parrafo_texto', 
             "Es crucial que la empresa articule y comunique consistentemente una propuesta de valor clara y diferenciada."))

def render_hoja_ruta(data):
    st.header(data.get('titulo_seccion_texto', "VII. Hoja de Ruta Estratégica: Iniciativas y Planes de Acción"))
    texto_sesion_trabajo = "Este cronograma es una visualización preliminar. Se recomienda desarrollar un Diagrama de Gantt más elaborado en la fase de planificación de la ejecución."
    sec_intro = data.get("introduccion_hoja_ruta", {})
    st.subheader(sec_intro.get('subtitulo_texto', "A. Introducción a la Hoja de Ruta"))
    st.write(sec_intro.get('parrafo_texto', 
             "La siguiente Hoja de Ruta traduce los Objetivos Estratégicos en Iniciativas y Planes de Acción concretos para los próximos 12-18 meses."))
    st.markdown("---")
    sec_detalle = data.get("detalle_por_objetivo", {})
    st.subheader(sec_detalle.get('subtitulo_texto', "B. Detalle de Iniciativas y Planes de Acción por Objetivo Estratégico"))
    for obj_hr in sec_detalle.get('lista_objetivos_con_detalle_data', []):
        st.markdown(f"#### {obj_hr.get('titulo_objetivo_pdf_style_texto', 'Objetivo Estratégico')}")
        st.caption(obj_hr.get('descripcion_detallada_objetivo_texto', ''))
        for inic_hr in obj_hr.get('iniciativas_estrategicas_data', []):
            with st.container(): 
                st.markdown(f"**Iniciativa {inic_hr.get('id_iniciativa_display_texto', '')}:** {inic_hr.get('titulo_iniciativa_texto', '')}")
                st.write(f"_{inic_hr.get('descripcion_detallada_iniciativa_texto', '')}_")
                st.markdown(f"**{inic_hr.get('titulo_planes_accion_display_texto', 'Planes de Acción Específicos:')}**")
                for plan_hr in inic_hr.get('planes_de_accion_data', []):
                    st.markdown(f"  • **{plan_hr.get('id_accion_display_texto', '')}:** {plan_hr.get('descripcion_accion_smart_texto', '')}")
                    st.markdown(f"    *Resp: {plan_hr.get('responsable_sugerido_texto', 'N/A')} | Plazo: {plan_hr.get('plazo_estimado_texto', 'N/A')} | KPI: {plan_hr.get('kpi_resultado_clave_texto', 'N/A')}*")
                st.markdown("---") 
    st.markdown("---")
    sec_cron = data.get("cronograma_general_hoja_ruta", {})
    st.subheader(sec_cron.get('subtitulo_texto', "C. Cronograma General de la Hoja de Ruta (Visualización Preliminar)")) 
    st.write(sec_cron.get('parrafo_intro_texto', ""))
    if sec_cron.get("tabla_cronograma_data"):
        try:
            df_cron = pd.DataFrame(sec_cron.get("tabla_cronograma_data", []))
            if not df_cron.empty:
                st.dataframe(df_cron, use_container_width=True)
            else:
                st.info(sec_cron.get('placeholder_texto', texto_sesion_trabajo))
        except Exception as e:
            st.error(f"Error al mostrar tabla de cronograma: {e}")
            st.info(sec_cron.get('placeholder_texto', texto_sesion_trabajo))
    else:
        st.info(sec_cron.get('placeholder_texto', texto_sesion_trabajo))
    st.caption(sec_cron.get('nota_plazos_texto', "CP: Corto Plazo (1-3 meses), MP: Mediano Plazo (4-9 meses), LP: Largo Plazo (10-18 meses)."))

def render_implementacion(data):
    st.header(data.get('titulo_seccion_texto', "VIII. Consideraciones para la Implementación y Gestión del Cambio"))
    texto_sesion_trabajo = "Esta sección requiere una discusión detallada y planificación. Se recomienda realizarla con los líderes de proceso y Eco Consultor."
    st.write(data.get('parrafo_intro_general_texto', 
             "La formulación de una estrategia sólida es solo el primer paso. El éxito real dependerá de una implementación efectiva y una gestión proactiva del cambio."))
    sec_factores = data.get("factores_criticos_exito", {})
    st.subheader(sec_factores.get('subtitulo_texto', "A. Factores Críticos de Éxito para la Implementación"))
    lista_factores = sec_factores.get('lista_factores_textos', [])
    if not lista_factores or "(Placeholder:" in sec_factores.get('parrafo_intro_texto', lista_factores[0] if lista_factores else ""):
        st.info(sec_factores.get('parrafo_intro_texto', texto_sesion_trabajo)) 
    else:
        st.write(sec_factores.get('parrafo_intro_texto', ""))
        for item in lista_factores: st.markdown(f"• {item}")
    st.markdown("---")
    sec_gob = data.get("gobernanza_seguimiento_sugerida", {})
    st.subheader(sec_gob.get('subtitulo_texto', "B. Estructura de Gobernanza y Seguimiento Sugerida"))
    parrafo_gob = sec_gob.get('parrafo_texto', "")
    if "(Placeholder:" in parrafo_gob or not parrafo_gob.strip():
        st.info(texto_sesion_trabajo)
    else:
        st.write(parrafo_gob)
    st.markdown("---")
    sec_gc = data.get("gestion_cambio_comunicacion", {})
    st.subheader(sec_gc.get('subtitulo_texto', "C. Gestión del Cambio y Comunicación"))
    parrafo_gc = sec_gc.get('parrafo_texto', "")
    if "(Placeholder:" in parrafo_gc or not parrafo_gc.strip():
        st.info(texto_sesion_trabajo)
    else:
        st.write(parrafo_gc)
    st.markdown("---")
    sec_rec = data.get("implicaciones_recursos_alto_nivel", {})
    st.subheader(sec_rec.get('subtitulo_texto', "D. Implicaciones de Recursos (Alto Nivel)"))
    parrafo_rec = sec_rec.get('parrafo_texto', "")
    if "(Placeholder:" in parrafo_rec or not parrafo_rec.strip():
        st.info(texto_sesion_trabajo)
    else:
        st.write(parrafo_rec)
    st.markdown("---")
    sec_riesgos = data.get("gestion_riesgos_estrategicos_implementacion", {})
    st.subheader(sec_riesgos.get('subtitulo_texto', "E. Gestión de Riesgos Estratégicos para la Implementación"))
    lista_riesgos = sec_riesgos.get('lista_riesgos_data', [])
    is_placeholder_riesgos = not lista_riesgos or \
                             (lista_riesgos and "(Placeholder:" in lista_riesgos[0].get("riesgo_texto", "")) or \
                             "(Placeholder:" in sec_riesgos.get('parrafo_intro_texto', "")
    if is_placeholder_riesgos:
        st.info(texto_sesion_trabajo)
    else:
        st.write(sec_riesgos.get('parrafo_intro_texto', ""))
        for riesgo_item in lista_riesgos:
            st.markdown(f"**Riesgo:** {riesgo_item.get('riesgo_texto', 'No especificado')}")
            st.markdown(f"  *Mitigación Sugerida:* {riesgo_item.get('mitigacion_texto', 'No especificada')}")
            
def render_conclusiones(data):
    st.header(data.get('titulo_seccion_texto', "IX. Conclusiones Finales y Próximos Pasos Recomendados"))
    texto_sesion_trabajo = "Se recomienda una sesión de trabajo para detallar estos próximos pasos y asegurar el compromiso del equipo."
    sec_con_gral = data.get("conclusion_general_textos_data", {})
    st.write(sec_con_gral.get('parrafo1_texto', 
             "El Diagnóstico de Planificación Estratégica ha proporcionado una evaluación integral de la madurez actual y ha sentado las bases para un crecimiento y fortalecimiento futuros."))
    st.write(sec_con_gral.get('parrafo2_texto', 
             "Es fundamental entender que la estrategia es un proceso continuo de aprendizaje, adaptación y ejecución."))
    st.markdown("---")
    
    # --- SECCIÓN DE RECOMENDACIONES (PROCESADA UNA SOLA VEZ) ---
    sec_rec90 = data.get("recomendaciones_proximos_90_dias_data", {})
    st.subheader(sec_rec90.get('subtitulo_texto', "A. Recomendaciones Específicas para los Próximos 90 Días"))
    
    parrafo_intro_recs = sec_rec90.get('parrafo_intro_texto', "")
    lista_recs = sec_rec90.get('lista_recomendaciones_textos', [])

    is_list_a_placeholder = False
    if lista_recs and len(lista_recs) == 1 and "(Placeholder:" in lista_recs[0]:
        is_list_a_placeholder = True

    if is_list_a_placeholder:
        st.write(parrafo_intro_recs) # Mostrar el párrafo introductorio
        st.info(lista_recs[0])      # Mostrar el texto del placeholder en st.info
    elif lista_recs: # Si hay recomendaciones reales
        st.write(parrafo_intro_recs)
        for item in lista_recs: 
            st.markdown(f"• {item}")
    else: # Si la lista está completamente vacía
        st.write(parrafo_intro_recs) 
        st.info(texto_sesion_trabajo) 
    # --- FIN SECCIÓN DE RECOMENDACIONES ---

    st.markdown("---") # Esta línea de separación es correcta
    
    sec_sesion = data.get("propuesta_sesion_acompanamiento_data", {})
    st.subheader(sec_sesion.get('subtitulo_texto', "B. Propuesta de Sesión de Trabajo y Acompañamiento"))
    st.write(sec_sesion.get('parrafo1_texto', 
             "ECO Consultores se pone a su disposición para facilitar una sesión de trabajo con el equipo directivo."))
    st.write(sec_sesion.get('parrafo2_texto', 
             "Asimismo, reiteramos nuestra disposición para acompañarlos en el proceso de ejecución de las iniciativas estratégicas."))
    st.markdown("---")
    sec_agrad = data.get("agradecimiento_final_data", {})
    st.subheader(sec_agrad.get('subtitulo_texto', "C. Agradecimiento Final"))
    st.write(sec_agrad.get('parrafo_texto', 
             "Agradecemos sinceramente a todo el equipo por su tiempo, apertura y colaboración durante el proceso de diagnóstico."))

# --- 5. ÁREA PRINCIPAL ---

# Verifica si hay datos JSON cargados. Usar .get() para evitar AttributeError si la clave no existe.
json_data_cargado = st.session_state.get('json_data', None)

if json_data_cargado is None:
    # Mostrar mensaje de error si existió un problema al cargar
    if st.session_state.get('error_carga', None):
        st.error(f"**Error al Cargar el Archivo:** {st.session_state.error_carga}")

    # Mensaje de bienvenida y logo
    st.markdown(f"<h1 style='text-align: center; color: {COLOR_TEXTO_TITULO_PRINCIPAL_CSS}; margin-top: 2rem;'>Bienvenido al {APP_TITLE}</h1>", unsafe_allow_html=True)

    if logo_base64:
        st.markdown(f"<div style='text-align: center; margin: 2rem 0;'><img src='data:image/png;base64,{logo_base64}' alt='Logo ECO' style='max-width: 150px; height: auto;'></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='text-align: center; font-size: 1.0em; color: {COLOR_TEXTO_SUTIL_CSS};'>(Logo ECO Consultores no disponible)</p>", unsafe_allow_html=True)

    st.markdown("<p style='text-align: center; font-size: 1.2em; margin-bottom: 2rem;'>Para comenzar, por favor cargue el archivo JSON del diagnóstico DPE utilizando el panel de la izquierda.</p>", unsafe_allow_html=True)
    st.info("ℹ️ **Instrucciones:** Use el botón 'Browse files' o arrastre un archivo JSON al área designada en la barra lateral.")

else: # Si hay datos JSON cargados
    json_data_main = json_data_cargado # Usar la variable obtenida con .get()
    METADATOS_INFORME = json_data_main.get("metadatos_informe", {})

    st.markdown(f"<h1>{METADATOS_INFORME.get('titulo_informe_base','Informe DPE')} para <b>{st.session_state.nombre_cliente}</b></h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: left; color: {COLOR_TEXTO_SUTIL_CSS}; font-size: 0.9em;'>Versión DPE: {METADATOS_INFORME.get('version_dpe', 'N/A')} | Fecha Diagnóstico: {METADATOS_INFORME.get('fecha_diagnostico', 'N/A')}</p>", unsafe_allow_html=True)
    #st.markdown("<hr>") # HR extra eliminada correctamente

    if st.session_state.get('show_json_data', False): # Usar .get() aquí también por seguridad
        with st.expander("Ver Datos JSON Crudos Cargados (Global)", expanded=False):
            st.json(json_data_main)
    
    tab_titles_map = {
        "Portada": "portada",
        "Resumen Ejecutivo": "resumen_ejecutivo",
        "Introducción": "introduccion_contexto",
        "Análisis Externo": "analisis_entorno_externo",
        "Diagnóstico Interno": "diagnostico_interno",
        "Síntesis FODA": "sintesis_estrategica_foda",
        "Formulación Estratégica": "formulacion_estrategica",
        "Hoja de Ruta": "hoja_ruta_estrategica",
        "Implementación": "consideraciones_implementacion",
        "Conclusiones": "conclusiones_finales",
        "Glosario": "glosario"
    }
    
    tabs_list = st.tabs(list(tab_titles_map.keys()))

    render_functions_map = {
        "portada": render_portada,
        "glosario": render_glosario,
        "resumen_ejecutivo": render_resumen_ejecutivo,
        "introduccion_contexto": render_introduccion_contexto,
        "analisis_entorno_externo": render_analisis_externo,
        "diagnostico_interno": render_diagnostico_interno,
        "sintesis_estrategica_foda": render_sintesis_foda,
        "formulacion_estrategica": render_formulacion_estrategica,
        "hoja_ruta_estrategica": render_hoja_ruta,
        "consideraciones_implementacion": render_implementacion,
        "conclusiones_finales": render_conclusiones
    }

    for i, tab_title_display in enumerate(tab_titles_map.keys()):
        with tabs_list[i]:
            data_key = tab_titles_map[tab_title_display]
            render_function = render_functions_map.get(data_key)
            data_for_section = json_data_main.get(data_key, {})

            if render_function:
                if data_for_section or data_key == "portada":
                    render_function(data_for_section)
                else:
                    st.warning(f"Datos para la sección '{tab_title_display}' (clave: '{data_key}') no encontrados o vacíos en el archivo JSON.")
                    render_function({})
            else:
                st.error(f"Función de renderizado no encontrada para la clave de datos: {data_key}")


# --- 6. PIE DE PÁGINA ---
st.markdown("<hr style='margin-top: 3rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)
version_dpe_footer_val = 'N/A'
if st.session_state.json_data and "metadatos_informe" in st.session_state.json_data:
    version_dpe_footer_val = st.session_state.json_data['metadatos_informe'].get('version_dpe', 'N/A')

footer_html = f"""
<div style="text-align: center; color: {COLOR_TEXTO_SUTIL_CSS}; font-size: 0.9em; padding-bottom:10px;">
    <p>© {datetime.date.today().year} ECO Consultores. Todos los derechos reservados.<br/>
    Herramienta de Diagnóstico de Planificación Estratégica (DPE) {version_dpe_footer_val}</p>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
