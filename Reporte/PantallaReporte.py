import streamlit as st
from Reporte.codigoRed.codigoRed import CodigoRed
from Reporte.Energia.Energia import Energia
from Reporte.pq.pq import PQ

def Reporte(report_id,cfe):
    # 1. Configuración de la página (DEBE ser el primer comando de Streamlit ejecutado en la app)
    # Nota: Si ya llamaste a set_page_config en tu archivo principal (main), debes quitar esto de aquí.
    st.set_page_config(
        page_title="Innova PQ Reporte",
        layout="wide", # 'wide' da más espacio para los reportes
        initial_sidebar_state="collapsed"
    )

    # 2. Inicializar la variable en el estado de la sesión para evitar el UnboundLocalError
    if "MostrarPanel" not in st.session_state:
        st.session_state.MostrarPanel = None

    # 3. Interfaz de Usuario: Título y Navegación
    st.title("📊 Panel de Reportes Innova PQ")
    st.markdown("Selecciona una pestaña para visualizar los datos correspondientes.")
    # Crear 3 columnas de igual tamaño para los botones

    col1, col2, col3, col4 = st.columns(4)



    # Botones que actualizan el session_state al hacer clic

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

        if st.button("📁Generar Archivos", use_container_width=True):

            st.session_state.MostrarPanel = "archivos"
            st.header("Gestión de Archivos")
            st.info("Aquí puedes procesar y descargar los reportes generados.")
            # Aquí puedes agregar botones de descarga o lógica de exportación
            if st.button("Preparar archivos para descarga"):
                st.success("Archivos listos para exportar.")

    st.divider() # Línea horizontal para separar el menú del contenido

    # 4. Renderizar el panel según el estado actual
    match st.session_state.MostrarPanel:
        case "codigo_red":
            return CodigoRed(report_id=report_id)
        case "energia":
            return Energia(report_id=report_id,cfe=cfe)
        case "pq":
            return PQ(report_id=report_id)
        case _:
            # Vista por defecto cuando no se ha seleccionado nada
            st.info("👈 Por favor, haz clic en uno de los botones de arriba para cargar un reporte o ir a la sección para generar archivos.")