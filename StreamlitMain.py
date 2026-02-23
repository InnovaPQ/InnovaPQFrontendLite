import streamlit as st
from Reporte.codigoRed.codigoRed import CodigoRed
from cargaDatos.cargaDatos2 import CargarDatos2
from Reporte.Energia.Energia import Energia
from Reporte.pq.pq import PQ
from Reporte.PantallaReporte import Reporte

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Carga de Reportes PQ",
    layout="wide"
)


# Lee el query param "report_id" de la URL
# Ejemplo: http://localhost:8501/?report_id=report04c8765d-90e9-467e-b67d-3beba4d58a7d&pagina=reporte
report_id = st.query_params.get("report_id")
pagina=st.query_params.get("pagina")


if pagina=="reporte":
    Reporte(report_id=report_id)
else:
    # Por defecto, mostrar la sección de carga
    CargarDatos2()

