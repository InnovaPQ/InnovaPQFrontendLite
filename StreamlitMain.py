import streamlit as st
from cargaDatos.cargaDatos2 import CargarDatos2
from Reporte.PantallaReporte import Reporte

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Carga de Reportes PQ",
    layout="wide"
)


# Lee el query param "report_id" de la URL
# Ejemplo: http://localhost:8501/?report_id=report04c8765d-90e9-467e-b67d-3beba4d58a7d&pagina=reporte&cfe=true
report_id = st.query_params.get("report_id")
pagina=st.query_params.get("pagina")
cfe=st.query_params.get("cfe")


if pagina=="reporte":
    Reporte(report_id=report_id,cfe=cfe)
else:
    # Por defecto, mostrar la sección de carga
    CargarDatos2()

