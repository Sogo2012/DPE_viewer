import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import io
import datetime
import base64
import os

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
APP_TITLE = "Visualizador Avanzado de Informes DPE - ECO Consultores"
LOGO_FILENAME = "Logo_ECO.png"
LOGO_DIRECTORY = "assets"
LOGO_PATH = os.path.join(LOGO_DIRECTORY, LOGO_FILENAME)

def get_image_as_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

logo_base64 = get_image_as_base64(LOGO_PATH)

try:
    page_icon_img = Image.open(LOGO_PATH)
except FileNotFoundError:
    page_icon_img = "📊"
    print(f"ADVERTENCIA (Favicon): Logo no encontrado en '{LOGO_PATH}'. Usando emoji.")

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=page_icon_img,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'mailto:soporte@ecoconsultores.com',
        'Report a bug': "mailto:soporte@ecoconsultores.com",
        'About': f"### {APP_TITLE}\nVersión 1.2\n\nDesarrollado con Streamlit."
    }
)

# --- 2. ESTILOS Y COLORES ---
COLOR_AZUL_ECO = "#173D4A"
COLOR_VERDE_ECO = "#66913E"
COLOR_GRIS_ECO = "#414549"
COLOR_TEXTO_TITULO_PRINCIPAL = COLOR_AZUL_ECO
COLOR_TEXTO_SUBTITULO_SECCION = COLOR_VERDE_ECO
COLOR_TEXTO_SUB_SUBTITULO = COLOR_GRIS_ECO
COLOR_TEXTO_CUERPO = "#333333"
COLOR_TEXTO_SUTIL = "#7f8c8d"
COLOR_FONDO_PAGINA = "#FFFFFF" # Blanco (para CSS, pero config.toml es mejor)
COLOR_TEXTO_BLANCO = "#FFFFFF"


st.markdown(f"""
<style>
    /* CSS para ajustes finos, el tema base se maneja mejor con config.toml */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 24px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6; 
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: {COLOR_TEXTO_CUERPO}; 
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLOR_VERDE_ECO};
        color: {COLOR_TEXTO_BLANCO}; 
    }}
    h1 {{ /* Ya definido en config.toml si se usa primaryColor/textColor */
        color: {COLOR_TEXTO_TITULO_PRINCIPAL};
    }}
    h2 {{
        color: {COLOR_TEXTO_SUBTITULO_SECCION};
        border-bottom: 2px solid {COLOR_VERDE_ECO};
        padding-bottom: 0.3rem;
    }}
    h3 {{
        color: {COLOR_TEXTO_SUB_SUBTITULO};
    }}
    /* Si config.toml no funciona, puedes intentar forzar el color del texto así:
    p, div, span, li, .stMarkdown, .stDataFrame, .stPlotlyChart {{
        color: {COLOR_TEXTO_CUERPO} !important;
    }}
    */
    hr {{
        margin-top: 0.5rem;
        margin-bottom: 1rem;
        border: 0;
        border-top: 1px solid rgba(0, 0, 0, 0.1);
    }}
</style>
""", unsafe_allow_html=True)


# --- 3. ESTADO DE LA APLICACIÓN ---
if 'json_data' not in st.session_state:
    st.session_state.json_data = None
if 'nombre_cliente' not in st.session_state:
    st.session_state.nombre_cliente = "Cliente"
if 'error_carga' not in st.session_state:
    st.session_state.error_carga = None
if 'show_json_data' not in st.session_state:
    st.session_state.show_json_data = False

# --- 4. BARRA LATERAL ---
with st.sidebar:
    if logo_base64:
        st.markdown(
            f'<div style="display: flex; justify-content: center; padding-bottom:10px;"><img src="data:image/png;base64,{logo_base64}" alt="Logo ECO Consultores" style="max-width: 80%; height: auto;"></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(f"<h2 style='color:{COLOR_AZUL_ECO}; text-align:center;'>ECO Consultores</h2>", unsafe_allow_html=True)
        print(f"ADVERTENCIA (Sidebar): Logo no encontrado en '{LOGO_PATH}'. Mostrando texto.")

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
                    string_data = string_data[1:]
                st.session_state.json_data = json.loads(string_data)
                st.session_state.error_carga = None
                if st.session_state.json_data and "metadatos_informe" in st.session_state.json_data:
                    nombre_cliente_json = st.session_state.json_data["metadatos_informe"].get("cliente_nombre")
                    st.session_state.nombre_cliente = nombre_cliente_json if nombre_cliente_json else "Cliente (Nombre no en JSON)"
                else:
                    st.session_state.nombre_cliente = "Cliente (Metadatos no en JSON)"
                st.success(f"✓ Archivo '{uploaded_file.name}' cargado para {st.session_state.nombre_cliente}.")
            except json.JSONDecodeError:
                st.session_state.error_carga = "Error de Decodificación: El archivo no es un JSON válido."
                st.session_state.json_data = None
            except Exception as e:
                st.session_state.error_carga = f"Error Crítico al procesar: {str(e)}."
                st.session_state.json_data = None

    if st.session_state.json_data:
        st.markdown("---")
        if st.button("🧹 Limpiar Datos y Reiniciar"):
            keys_to_delete = list(st.session_state.keys())
            for key in keys_to_delete: del st.session_state[key]
            st.rerun()
        st.session_state.show_json_data = st.toggle("Mostrar datos JSON crudos", value=st.session_state.show_json_data)


# --- MOVER AQUÍ LAS DEFINICIONES DE FUNCIONES DE RENDERIZADO ---
def render_portada(data):
    st.markdown(f"<div style='padding: 20px; text-align:center;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color: {COLOR_TEXTO_TITULO_PRINCIPAL}; font-size: 2.5em; margin-top: 50px;'>{data.get('titulo_principal_texto', 'Título Portada')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 1.8em; color: {COLOR_TEXTO_TITULO_PRINCIPAL};'>{data.get('preparado_para_texto', 'Preparado para:')} <b style='color:{COLOR_VERDE_ECO}'>{data.get('nombre_cliente_texto', st.session_state.nombre_cliente)}</b></p>", unsafe_allow_html=True)
    
    # Obtener METADATOS_INFORME aquí si es necesario, o pasarlo como argumento
    metadatos_informe_local = st.session_state.json_data.get("metadatos_informe", {}) if st.session_state.json_data else {}
    st.markdown(f"<p style='font-size: 1.1em; color: {COLOR_GRIS_ECO}; margin-bottom: 100px;'>{data.get('fecha_diagnostico_texto', metadatos_informe_local.get('fecha_diagnostico', 'N/A'))}</p>", unsafe_allow_html=True)

    try:
        img_portada = Image.open(LOGO_PATH)
        st.image(img_portada, width=250)
    except FileNotFoundError:
        st.markdown(f"<p style='font-size: 0.8em; color: {COLOR_TEXTO_SUTIL};'>(Logo de portada no encontrado en '{LOGO_PATH}')</p>", unsafe_allow_html=True)

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
            st.markdown("---", help="Separador de término")

def render_resumen_ejecutivo(data_re):
    st.header(data_re.get('titulo_seccion_texto', 'I. Resumen Ejecutivo Gerencial'))

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
            # Convertir color HEX a RGBA para Plotly
            r, g, b = tuple(int(COLOR_VERDE_ECO.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            fill_color_rgba = f'rgba({r}, {g}, {b}, 0.6)'

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
                                     tickfont=dict(size=10, color=COLOR_TEXTO_CUERPO))
                ),
                title=dict(text=sec_madurez_global.get("grafico_radar_titulo_sugerido", "Nivel de Madurez por Área (%)"),
                           x=0.5, font=dict(size=16, color=COLOR_TEXTO_TITULO_PRINCIPAL)),
                showlegend=False, height=450, margin=dict(l=50, r=50, t=80, b=50),
                paper_bgcolor='rgba(255,255,255,0)', plot_bgcolor='rgba(255,255,255,0)', # Fondos transparentes para tema Streamlit
                font=dict(color=COLOR_TEXTO_CUERPO, size=11)
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            st.caption(sec_madurez_global.get("grafico_radar_caption_texto", ""))
        else:
            st.caption("Datos para gráfico radar incompletos o con formato incorrecto.")
    else:
        st.caption("Datos para gráfico radar no disponibles o insuficientes.")

    for sub_key in ["hallazgos_area", "foda_interno", "foda_externo", "lineamientos_estrategicos", "conclusion_resumen_ejecutivo"]:
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
        if key != 'subtitulo_texto' and isinstance(val, str):
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
    st.markdown(f"**{seccion_alcance.get('proceso_recoleccion_titulo_texto','Proceso:')}**")
    for item in seccion_alcance.get('lista_metodologia_textos', []): st.markdown(f"• {item}")
    st.caption(seccion_alcance.get('parrafo_limitaciones_texto', ""))

def render_analisis_externo(data):
    st.header(data.get('titulo_seccion_texto', "III. Análisis del Entorno Externo"))
    sec_macro = data.get("macroentorno", {})
    st.subheader(sec_macro.get('subtitulo_texto', "A. Análisis del Macroentorno"))
    st.write(sec_macro.get('parrafo_intro_indicadores_texto', ""))
    if sec_macro.get("grafico_bccr_data"):
        df_bccr = pd.DataFrame(sec_macro["grafico_bccr_data"])
        if not df_bccr.empty and 'Fecha' in df_bccr.columns:
            try:
                df_bccr['Fecha'] = pd.to_datetime(df_bccr['Fecha'])
                # Asegurarse que las columnas existan y sean numéricas
                cols_to_plot_bccr = []
                if 'Tasa_Basica_Pasiva' in df_bccr.columns:
                    df_bccr['Tasa_Basica_Pasiva'] = pd.to_numeric(df_bccr['Tasa_Basica_Pasiva'], errors='coerce')
                    cols_to_plot_bccr.append('Tasa_Basica_Pasiva')
                if 'Tipo_Cambio_Venta_Referencia' in df_bccr.columns:
                    df_bccr['Tipo_Cambio_Venta_Referencia'] = pd.to_numeric(df_bccr['Tipo_Cambio_Venta_Referencia'], errors='coerce')
                    cols_to_plot_bccr.append('Tipo_Cambio_Venta_Referencia')

                if cols_to_plot_bccr:
                    fig_bccr = px.line(df_bccr, x='Fecha', y=cols_to_plot_bccr,
                                       title=sec_macro.get("grafico_bccr_titulo_sugerido", "Indicadores BCCR"),
                                       labels={'value': 'Valor', 'variable': 'Indicador'})
                    fig_bccr.update_layout(
                        yaxis_title='Tasa (%) / Tipo de Cambio (CRC)',
                        legend_title_text='Indicadores',
                        paper_bgcolor='rgba(255,255,255,0)', plot_bgcolor='rgba(255,255,255,0)',
                        font_color=COLOR_TEXTO_CUERPO
                    )
                    st.plotly_chart(fig_bccr, use_container_width=True)
                    st.caption(sec_macro.get("grafico_bccr_caption_texto", ""))
                else:
                    st.info("Columnas de datos para gráfico BCCR no encontradas (TBP o TC).")
            except Exception as e:
                st.error(f"Error al procesar datos para gráfico BCCR: {e}")
                st.json(sec_macro["grafico_bccr_data"]) # Mostrar datos si falla el parseo
        else: st.info("Datos para gráfico BCCR no disponibles o en formato incorrecto.")
    st.markdown("---")

    sec_cfia = data.get("sector_industria_cfia", {})
    st.subheader(sec_cfia.get('subtitulo_texto', "B. Análisis del Sector/Industria"))
    st.write(sec_cfia.get('parrafo_intro_texto', ""))

    # Gráfico Tendencia M2 CFIA
    tend_data = sec_cfia.get("grafico_tendencia_m2_data", {})
    if tend_data.get("historico") and tend_data.get("actual_proyeccion"):
        try:
            df_hist = pd.DataFrame(tend_data["historico"])
            df_proy = pd.DataFrame(tend_data["actual_proyeccion"])
            df_real = pd.DataFrame(tend_data.get("actual_real", []))

            fig_tend = go.Figure()
            for col in df_hist.columns:
                if col != 'Mes':
                    fig_tend.add_trace(go.Scatter(x=df_hist['Mes'], y=df_hist[col], mode='lines+markers', name=f'Hist. {col}'))
            if not df_real.empty and 'Mes' in df_real.columns and 'Valor_Actual' in df_real.columns:
                 # Filtrar ceros para no cortar la línea si hay meses futuros con 0
                df_real_plot = df_real[df_real['Valor_Actual'] > 0]
                if not df_real_plot.empty:
                    fig_tend.add_trace(go.Scatter(x=df_real_plot['Mes'], y=df_real_plot['Valor_Actual'], mode='lines+markers', name='Actual Real', line=dict(color='black', width=2)))
            
            # Conectar real con proyección si es necesario
            if not df_real.empty and not df_proy.empty and 'Mes' in df_proy.columns and 'Valor_Proyeccion' in df_proy.columns:
                # Tomar el último mes real con datos
                last_real_month_df = df_real[df_real['Valor_Actual'] > 0]
                if not last_real_month_df.empty:
                    last_real_month_name = last_real_month_df['Mes'].iloc[-1]
                    last_real_value = last_real_month_df['Valor_Actual'].iloc[-1]
                    
                    # Encontrar el índice de ese mes en la proyección
                    if last_real_month_name in df_proy['Mes'].values:
                        idx_proy_start = df_proy[df_proy['Mes'] == last_real_month_name].index[0]
                        # Crear un punto de conexión
                        df_proy_plot = pd.concat([
                            pd.DataFrame([{'Mes': last_real_month_name, 'Valor_Proyeccion': last_real_value}]),
                            df_proy.iloc[idx_proy_start+1:] 
                        ], ignore_index=True) if idx_proy_start + 1 < len(df_proy) else pd.DataFrame([{'Mes': last_real_month_name, 'Valor_Proyeccion': last_real_value}])
                        
                        fig_tend.add_trace(go.Scatter(x=df_proy_plot['Mes'], y=df_proy_plot['Valor_Proyeccion'], mode='lines+markers', name='Proyección', line=dict(dash='dash', color='red')))
                    else: # Si no hay superposición directa, graficar la proyección completa
                         fig_tend.add_trace(go.Scatter(x=df_proy['Mes'], y=df_proy['Valor_Proyeccion'], mode='lines+markers', name='Proyección', line=dict(dash='dash', color='red')))
                else: # Si no hay datos reales, graficar la proyección completa
                    fig_tend.add_trace(go.Scatter(x=df_proy['Mes'], y=df_proy['Valor_Proyeccion'], mode='lines+markers', name='Proyección', line=dict(dash='dash', color='red')))


            fig_tend.update_layout(title=sec_cfia.get("grafico_tendencia_m2_titulo_sugerido"),
                                   xaxis_title='Mes', yaxis_title='M² Construidos',
                                   paper_bgcolor='rgba(255,255,255,0)', plot_bgcolor='rgba(255,255,255,0)', font_color=COLOR_TEXTO_CUERPO)
            st.plotly_chart(fig_tend, use_container_width=True)
            st.caption(sec_cfia.get("grafico_tendencia_m2_caption_texto"))
        except Exception as e:
            st.error(f"Error al generar gráfico de tendencia CFIA: {e}")
            st.json(tend_data)
    
    # ... (resto de render_analisis_externo, render_diagnostico_interno, etc., como en la respuesta anterior) ...
    # ... (asegurándote de que las claves del JSON coincidan con las que usas) ...
    # C. Análisis Competencia
    sec_comp = data.get("analisis_competencia", {})
    st.subheader(sec_comp.get('subtitulo_texto', "C. Análisis de la Competencia"))
    st.write(sec_comp.get('parrafo_intro_texto', ""))
    for i, comp in enumerate(sec_comp.get('lista_competidores_data', [])):
        with st.expander(f"{comp.get('id_competidor_display_texto', 'Competidor ' + str(i+1))}: {comp.get('nombre_y_url_texto', '').split('(')[0].strip()}", expanded=i==0):
            st.markdown(f"**URL:** {comp.get('nombre_y_url_texto', '')}")
            st.markdown(f"**Giro Principal:** {comp.get('giro_principal_inferido_texto', 'N/A')}")
            st.markdown(f"**Productos/Servicios Clave:** {comp.get('productos_servicios_clave_texto', 'N/A')}")
            st.markdown(f"**Propuesta de Valor:** {comp.get('propuesta_valor_observada_texto', 'N/A')}")
            st.markdown(f"**{comp.get('fortalezas_clave_titulo_texto', 'Fortalezas:')}**")
            for f_item in comp.get('fortalezas_clave_lista_textos', []): st.markdown(f"• {f_item}")
    st.caption(sec_comp.get('nota_adicionales_texto', ""))
    st.markdown("---")

    # D. Huella Digital
    sec_huella = data.get("huella_digital_ecosistema", {})
    st.subheader(sec_huella.get('subtitulo_texto', "D. Huella Digital"))
    st.markdown(f"**{sec_huella.get('cliente_titulo_texto', 'Huella Cliente')}**")
    st.write(sec_huella.get('cliente_evaluacion_sitio_texto', ""))
    st.caption(sec_huella.get('cliente_palabras_clave_sugeridas_texto', ""))
    st.markdown(f"**{sec_huella.get('ecosistema_titulo_texto', 'Ecosistema Sector')}**")
    st.write(sec_huella.get('ecosistema_google_trends_intro_texto', ""))
    for item in sec_huella.get('ecosistema_google_trends_lista_textos', []): st.markdown(f"• {item}")
    st.markdown("---")

    # E. Síntesis Oportunidades y Amenazas Externas
    sec_sint_ext = data.get("sintesis_oportunidades_amenazas_externas", {})
    st.subheader(sec_sint_ext.get('subtitulo_texto', "E. Síntesis Externa"))
    st.markdown(f"**{sec_sint_ext.get('oportunidades_titulo_texto', 'Oportunidades:')}**")
    for item in sec_sint_ext.get('oportunidades_lista_textos', []): st.markdown(f"• {item}")
    st.markdown(f"**{sec_sint_ext.get('amenazas_titulo_texto', 'Amenazas:')}**")
    for item in sec_sint_ext.get('amenazas_lista_textos', []): st.markdown(f"• {item}")


def render_diagnostico_interno(data):
    st.header(data.get('titulo_seccion_texto', "IV. Diagnóstico Interno"))
    sec_mad_glob = data.get("madurez_global_organizacion", {})
    st.subheader(sec_mad_glob.get('subtitulo_texto', "A. Madurez Global"))
    st.write(sec_mad_glob.get('parrafo_puntuacion_texto', ""))
    st.write(sec_mad_glob.get('parrafo_explicacion_texto', ""))
    st.markdown("---")

    sec_eval_areas = data.get("evaluacion_detallada_areas", {})
    st.subheader(sec_eval_areas.get('subtitulo_texto', "B. Evaluación por Áreas"))
    for area_data in sec_eval_areas.get('lista_areas_evaluacion_data', []):
        with st.expander(area_data.get('titulo_area_display_pdf_style', "Área"), expanded=True):
            st.write(area_data.get('nivel_madurez_display_texto', ""))
            graf_data = area_data.get('grafico_barra_madurez_data', {})
            if graf_data.get('label') and graf_data.get('value') is not None:
                try:
                    value = float(graf_data['value'])
                    df_bar = pd.DataFrame([{'Área': graf_data['label'], 'Madurez (%)': value}])
                    fig_bar = px.bar(df_bar, x='Madurez (%)', y='Área', orientation='h', range_x=[0,100],
                                     color_discrete_sequence=[COLOR_VERDE_ECO])
                    fig_bar.update_layout(height=150, margin=dict(l=10, r=10, t=30, b=10),
                                          title_text=area_data.get('grafico_barra_madurez_caption_texto', ""), title_x=0.5,
                                          paper_bgcolor='rgba(255,255,255,0)', plot_bgcolor='rgba(255,255,255,0)', font_color=COLOR_TEXTO_CUERPO)
                    st.plotly_chart(fig_bar, use_container_width=True)
                except ValueError:
                    st.warning(f"Valor no numérico para gráfico de barra: {graf_data['value']}")


            st.markdown(f"**{area_data.get('interpretacion_negocio_titulo_texto', 'Interpretación:')}**")
            st.write(area_data.get('interpretacion_negocio_parrafo_texto', ""))
            st.markdown(f"**{area_data.get('fortalezas_clave_titulo_texto', 'Fortalezas:')}**")
            for f_item in area_data.get('fortalezas_clave_lista_data', []):
                st.markdown(f"• {f_item.get('criterio_texto', '')} {f_item.get('nivel_texto', '')}")
            st.markdown(f"**{area_data.get('oportunidades_mejora_titulo_texto', 'Oportunidades:')}**")
            st.write(area_data.get('oportunidades_mejora_resumen_texto', ""))
    st.markdown("---")

    sec_sint_int = data.get("sintesis_foda_interna", {})
    st.subheader(sec_sint_int.get('subtitulo_texto', "C. Síntesis Interna"))
    st.markdown(f"**{sec_sint_int.get('fortalezas_titulo_texto', 'Fortalezas:')}**")
    for item in sec_sint_int.get('fortalezas_lista_textos', []): st.markdown(f"• {item}")
    st.markdown(f"**{sec_sint_int.get('debilidades_titulo_texto', 'Debilidades:')}**")
    for item in sec_sint_int.get('debilidades_lista_textos', []): st.markdown(f"• {item}")


def render_sintesis_foda(data):
    st.header(data.get('titulo_seccion_texto', "V. Síntesis Estratégica FODA"))
    sec_matriz = data.get("matriz_foda_integrada", {})
    st.subheader(sec_matriz.get('subtitulo_texto', "A. Matriz FODA"))
    st.write(sec_matriz.get('parrafo_intro_texto', ""))
    foda_data = sec_matriz.get('tabla_foda_data', {})
    if foda_data:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"#### {sec_matriz.get('titulos_cuadrantes_foda_textos', {}).get('fortalezas', 'FORTALEZAS')}")
            for item in foda_data.get('fortalezas_lista_textos', []): st.markdown(f"• {item}")
            st.markdown("---")
            st.markdown(f"#### {sec_matriz.get('titulos_cuadrantes_foda_textos', {}).get('oportunidades', 'OPORTUNIDADES')}")
            for item in foda_data.get('oportunidades_lista_textos', []): st.markdown(f"• {item}")
        with col2:
            st.markdown(f"#### {sec_matriz.get('titulos_cuadrantes_foda_textos', {}).get('debilidades', 'DEBILIDADES')}")
            for item in foda_data.get('debilidades_lista_textos', []): st.markdown(f"• {item}")
            st.markdown("---")
            st.markdown(f"#### {sec_matriz.get('titulos_cuadrantes_foda_textos', {}).get('amenazas', 'AMENAZAS')}")
            for item in foda_data.get('amenazas_lista_textos', []): st.markdown(f"• {item}")
    st.markdown("---")
    sec_tows = data.get("analisis_cruzado_tows", {})
    st.subheader(sec_tows.get('subtitulo_texto', "B. Análisis TOWS"))
    st.info(sec_tows.get('parrafo_placeholder_texto', "Análisis TOWS pendiente."))
    st.markdown("---")
    sec_desafios = data.get("desafios_estrategicos_clave", {})
    st.subheader(sec_desafios.get('subtitulo_texto', "C. Desafíos Estratégicos"))
    st.info(sec_desafios.get('parrafo_placeholder_texto', "Desafíos estratégicos pendientes."))

def render_formulacion_estrategica(data):
    st.header(data.get('titulo_seccion_texto', "VI. Formulación Estratégica"))
    sec_identidad = data.get("identidad_estrategica", {})
    st.subheader(sec_identidad.get('subtitulo_texto', "A. Identidad Estratégica"))
    st.write(sec_identidad.get('parrafo_introductorio_texto', ""))
    st.markdown(f"**Misión Sugerida:** {sec_identidad.get('mision_sugerida_texto', 'N/A')}")
    st.markdown(f"**Visión Sugerida:** {sec_identidad.get('vision_sugerida_texto', 'N/A')}")
    st.markdown(f"**{sec_identidad.get('titulo_valores_sugeridos_texto', 'Valores:')}**")
    for val in sec_identidad.get('lista_valores_sugeridos_textos', []): st.markdown(f"• {val}")
    st.markdown("---")
    sec_obj = data.get("objetivos_estrategicos_prioritarios", {})
    st.subheader(sec_obj.get('subtitulo_texto', "B. Objetivos Estratégicos"))
    st.write(sec_obj.get('parrafo_intro_texto', ""))
    for i, obj_data in enumerate(sec_obj.get('lista_objetivos_data', [])):
        st.markdown(f"**{obj_data.get('id_display_pdf_style', 'Objetivo ' + str(i+1))}: {obj_data.get('titulo_objetivo_texto', '')}**")
        st.caption(obj_data.get('descripcion_detallada_texto', ''))
        st.markdown(f"_{obj_data.get('kpis_metas_titulo_texto', 'KPIs:')}_ {obj_data.get('kpis_metas_contenido_texto', '')}")
        st.markdown(f"_{obj_data.get('alineacion_desafios_titulo_texto', 'Alineación:')}_ {obj_data.get('alineacion_desafios_contenido_texto', '')}")
    st.markdown("---")
    sec_prop_valor = data.get("propuesta_valor_diferenciada", {})
    st.subheader(sec_prop_valor.get('subtitulo_texto', "C. Propuesta de Valor"))
    st.write(sec_prop_valor.get('parrafo_texto', ""))

def render_hoja_ruta(data):
    st.header(data.get('titulo_seccion_texto', "VII. Hoja de Ruta Estratégica"))
    sec_intro = data.get("introduccion_hoja_ruta", {})
    st.subheader(sec_intro.get('subtitulo_texto', "A. Introducción"))
    st.write(sec_intro.get('parrafo_texto', ""))
    st.markdown("---")
    sec_detalle = data.get("detalle_por_objetivo", {})
    st.subheader(sec_detalle.get('subtitulo_texto', "B. Detalle por Objetivo"))
    for obj_hr in sec_detalle.get('lista_objetivos_con_detalle_data', []):
        st.markdown(f"#### {obj_hr.get('titulo_objetivo_pdf_style_texto', 'Objetivo')}")
        st.caption(obj_hr.get('descripcion_detallada_objetivo_texto', ''))
        for inic_hr in obj_hr.get('iniciativas_estrategicas_data', []):
            with st.container():
                st.markdown(f"**Iniciativa {inic_hr.get('id_iniciativa_display_texto', '')}:** {inic_hr.get('titulo_iniciativa_texto', '')}")
                st.write(f"_{inic_hr.get('descripcion_detallada_iniciativa_texto', '')}_")
                st.markdown(f"**{inic_hr.get('titulo_planes_accion_display_texto', 'Planes:')}**")
                for plan_hr in inic_hr.get('planes_de_accion_data', []):
                    st.markdown(f"  • **{plan_hr.get('id_accion_display_texto', '')}:** {plan_hr.get('descripcion_accion_smart_texto', '')}")
                    st.markdown(f"    *Resp: {plan_hr.get('responsable_sugerido_texto', 'N/A')} | Plazo: {plan_hr.get('plazo_estimado_texto', 'N/A')} | KPI: {plan_hr.get('kpi_resultado_clave_texto', 'N/A')}*")
    st.markdown("---")
    sec_cron = data.get("cronograma_general_hoja_ruta", {})
    st.subheader(sec_cron.get('subtitulo_texto', "D. Cronograma General"))
    st.write(sec_cron.get('parrafo_intro_texto', ""))
    if sec_cron.get("tabla_cronograma_data"):
        df_cron = pd.DataFrame(sec_cron.get("tabla_cronograma_data", []))
        st.dataframe(df_cron, use_container_width=True)
    st.caption(sec_cron.get('nota_plazos_texto', ""))

def render_implementacion(data):
    st.header(data.get('titulo_seccion_texto', "VIII. Consideraciones para la Implementación"))
    st.write(data.get('parrafo_intro_general_texto', ""))
    sec_factores = data.get("factores_criticos_exito", {})
    st.subheader(sec_factores.get('subtitulo_texto', "A. Factores Críticos"))
    st.write(sec_factores.get('parrafo_intro_texto', ""))
    for item in sec_factores.get('lista_factores_textos', []): st.markdown(f"• {item}")
    st.markdown("---")
    sec_gob = data.get("gobernanza_seguimiento_sugerida", {})
    st.subheader(sec_gob.get('subtitulo_texto', "B. Gobernanza"))
    st.write(sec_gob.get('parrafo_texto', ""))
    st.markdown("---")
    sec_gc = data.get("gestion_cambio_comunicacion", {})
    st.subheader(sec_gc.get('subtitulo_texto', "C. Gestión del Cambio"))
    st.write(sec_gc.get('parrafo_texto', ""))
    st.markdown("---")
    sec_rec = data.get("implicaciones_recursos_alto_nivel", {})
    st.subheader(sec_rec.get('subtitulo_texto', "D. Implicaciones Recursos"))
    st.write(sec_rec.get('parrafo_texto', ""))
    st.markdown("---")
    sec_riesgos = data.get("gestion_riesgos_estrategicos_implementacion", {})
    st.subheader(sec_riesgos.get('subtitulo_texto', "E. Gestión Riesgos"))
    st.write(sec_riesgos.get('parrafo_intro_texto', ""))
    for riesgo_item in sec_riesgos.get('lista_riesgos_data', []):
        st.markdown(f"**Riesgo:** {riesgo_item.get('riesgo_texto', '')}")
        st.markdown(f"  *Mitigación:* {riesgo_item.get('mitigacion_texto', '')}")

def render_conclusiones(data):
    st.header(data.get('titulo_seccion_texto', "IX. Conclusiones Finales"))
    sec_con_gral = data.get("conclusion_general_textos_data", {})
    st.write(sec_con_gral.get('parrafo1_texto', ""))
    st.write(sec_con_gral.get('parrafo2_texto', ""))
    st.markdown("---")
    sec_rec90 = data.get("recomendaciones_proximos_90_dias_data", {})
    st.subheader(sec_rec90.get('subtitulo_texto', "Recomendaciones 90 Días"))
    st.write(sec_rec90.get('parrafo_intro_texto', ""))
    for item in sec_rec90.get('lista_recomendaciones_textos', []): st.markdown(f"• {item}")
    st.markdown("---")
    sec_sesion = data.get("propuesta_sesion_acompanamiento_data", {})
    st.subheader(sec_sesion.get('subtitulo_texto', "Propuesta Sesión"))
    st.write(sec_sesion.get('parrafo1_texto', ""))
    st.write(sec_sesion.get('parrafo2_texto', ""))
    st.markdown("---")
    sec_agrad = data.get("agradecimiento_final_data", {})
    st.subheader(sec_agrad.get('subtitulo_texto', "Agradecimiento"))
    st.write(sec_agrad.get('parrafo_texto', ""))

# --- 5. ÁREA PRINCIPAL ---
# (El if/else que decide si mostrar bienvenida o contenido del informe ya está arriba)
# (La sección que llama a las funciones de renderizado también está arriba, DESPUÉS de definirlas)

if st.session_state.json_data is None:
    if st.session_state.error_carga:
        st.error(f"**Error al Cargar el Archivo:** {st.session_state.error_carga}")

    st.markdown(f"<h1 style='text-align: center; color: {COLOR_TEXTO_TITULO_PRINCIPAL}; margin-top: 2rem;'>Bienvenido al {APP_TITLE}</h1>", unsafe_allow_html=True)

    if logo_base64:
        st.markdown(f"<div style='text-align: center; margin: 2rem 0;'><img src='data:image/png;base64,{logo_base64}' alt='Logo ECO' style='max-width: 150px; height: auto;'></div>", unsafe_allow_html=True)

    st.markdown("<p style='text-align: center; font-size: 1.2em; margin-bottom: 2rem;'>Para comenzar, por favor cargue el archivo JSON del diagnóstico DPE utilizando el panel de la izquierda.</p>", unsafe_allow_html=True)
    st.info("ℹ️ **Instrucciones:** Use el botón 'Browse files' o arrastre un archivo JSON al área designada en la barra lateral.")
else:
    json_data_main = st.session_state.json_data
    METADATOS_INFORME = json_data_main.get("metadatos_informe", {})

    st.markdown(f"<h1 style='color:{COLOR_TEXTO_TITULO_PRINCIPAL};'>{METADATOS_INFORME.get('titulo_informe_base','Informe DPE')} para <b>{st.session_state.nombre_cliente}</b></h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: left; color: {COLOR_TEXTO_SUTIL}; font-size: 0.9em;'>Versión DPE: {METADATOS_INFORME.get('version_dpe', 'N/A')} | Fecha Diagnóstico: {METADATOS_INFORME.get('fecha_diagnostico', 'N/A')}</p>", unsafe_allow_html=True)
    st.markdown("<hr>")

    if st.session_state.show_json_data:
        with st.expander("Ver Datos JSON Crudos Cargados (Global)", expanded=False):
            st.json(json_data_main)

    tab_titles = [
        "Portada", "Glosario", "I. Resumen Ejecutivo", "II. Introducción",
        "III. Análisis Externo", "IV. Diagnóstico Interno", "V. Síntesis FODA",
        "VI. Formulación Estratégica", "VII. Hoja de Ruta", "VIII. Implementación", "IX. Conclusiones"
    ]
    tabs = st.tabs(tab_titles)

    with tabs[0]: render_portada(json_data_main.get("portada", {}))
    with tabs[1]: render_glosario(json_data_main.get("glosario", {}))
    with tabs[2]: render_resumen_ejecutivo(json_data_main.get("resumen_ejecutivo", {}))
    with tabs[3]: render_introduccion_contexto(json_data_main.get("introduccion_contexto", {}))
    with tabs[4]: render_analisis_externo(json_data_main.get("analisis_entorno_externo", {}))
    with tabs[5]: render_diagnostico_interno(json_data_main.get("diagnostico_interno", {}))
    with tabs[6]: render_sintesis_foda(json_data_main.get("sintesis_estrategica_foda", {}))
    with tabs[7]: render_formulacion_estrategica(json_data_main.get("formulacion_estrategica", {}))
    with tabs[8]: render_hoja_ruta(json_data_main.get("hoja_ruta_estrategica", {}))
    with tabs[9]: render_implementacion(json_data_main.get("consideraciones_implementacion", {}))
    with tabs[10]: render_conclusiones(json_data_main.get("conclusiones_finales", {}))


# --- 6. PIE DE PÁGINA ---
st.markdown("<hr style='margin-top: 3rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)
version_dpe_footer_val = st.session_state.json_data.get('metadatos_informe', {}).get('version_dpe', 'N/A') if st.session_state.json_data else 'N/A'
footer_html = f"""
<div style="text-align: center; color: {COLOR_TEXTO_SUTIL}; font-size: 0.9em; padding-bottom:10px;">
    <p>© {datetime.date.today().year} ECO Consultores. Todos los derechos reservados.<br/>
    Herramienta de Diagnóstico de Planificación Estratégica (DPE) {version_dpe_footer_val}</p>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)

