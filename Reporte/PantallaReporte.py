import streamlit as st
from Reporte.codigoRed.codigoRed import CodigoRed
from Reporte.Energia.Energia import Energia
from Reporte.pq.pq import PQ
from Reporte.GenerarArchivos.GenerarArchivos import GenerarArchivos
# IMPORTANTE: Asegúrate de importar la función que creamos en el paso anterior
# from tu_archivo_utilidades import modal_generacion_pdf_unificado

def Reporte(report_id, cfe): 
    # Nota: Agregué 'servicio' y 'datos' a los argumentos de la función para poder 
    # pasarlos al modal de generación de PDFs.
    
    # 1. Configuración de la página
    # st.set_page_config(page_title="Innova PQ Reporte", layout="wide", initial_sidebar_state="collapsed")
    # (Te recomiendo mover el set_page_config a tu archivo principal main.py si es posible)

    # 2. Inicializar la variable en el estado de la sesión
    if "MostrarPanel" not in st.session_state:
        st.session_state.MostrarPanel = None

    # 3. Interfaz de Usuario: Título y Navegación
    st.title("📊 Panel de Reportes Innova PQ")
    st.markdown("Selecciona una pestaña para visualizar los datos correspondientes.")
    
    # Crear 4 columnas de igual tamaño para los botones
    col1, col2, col3, col4 = st.columns(4)

    # Botones limpios: Su ÚNICO trabajo es actualizar el st.session_state
    with col1:
        if st.button("🔌 Código de Red", use_container_width=True):
            st.session_state.MostrarPanel = "codigo_red"

    with col2:
        if st.button("⚡ Reporte de Energía", use_container_width=True):
            st.session_state.MostrarPanel = "energia"

    with col3:
        if st.button("📈 Reporte PQ", use_container_width=True):
            st.session_state.MostrarPanel = "pq"

    with col4:
        if st.button("📁 Generar Archivos", use_container_width=True):
            st.session_state.MostrarPanel = "archivos"

    st.divider() # Línea horizontal para separar el menú del contenido

    # 4. Renderizar el panel según el estado actual
    match st.session_state.MostrarPanel:
        case "codigo_red":
            return CodigoRed(report_id=report_id)
            
        case "energia":
            return Energia(report_id=report_id, cfe=cfe)
            
        case "pq":
            return PQ(report_id=report_id)
            
        case "archivos":
            return GenerarArchivos(report_id=report_id,cfe=cfe)
 
        case _:
            # Vista por defecto (cuando MostrarPanel es None o no coincide)
            st.info("👈 Por favor, haz clic en uno de los botones de arriba para cargar un reporte o ir a la sección para generar archivos.")