import streamlit as st
from Modelos import Tabla




def Cumplimiento(Servicio,Datos):

    # --- Tabla cumplimiento ---
    with st.container():
        rutaTablaCumplimiento=Datos["CumplimientoRed"]["Principal"]
        TablaCumplimiento=Tabla("Tabla de cumplimiento",rutaDatos=rutaTablaCumplimiento,servicio=Servicio)
        TablaCumplimiento.construirContenedor()

    with st.expander(label="Cumplimiento de armónicos de corriente"):
        rutaTablaArmonicosP95=Datos["ArmonicosCorriente"]["ArmonicosITablaP95"]
        TablaArmonicosP95=Tabla("Niveles de armónicos de corriente (P95)",rutaDatos=rutaTablaArmonicosP95,servicio=Servicio)
        TablaArmonicosP95.construirContenedor()


    with st.expander(label="Límites aplicables"):
        rutaTablaAplicables=Datos["CumplimientoRed"]["limaplicables"]
        TablaAplicables=Tabla("Código de red al centro de carga",rutaDatos=rutaTablaAplicables,servicio=Servicio)
        TablaAplicables.construirContenedor()

        rutaTablaLimdatad=Datos["CumplimientoRed"]["limdatd"]
        TablaAplicables=Tabla("DATD y DAI",rutaDatos=rutaTablaLimdatad,servicio=Servicio)
        TablaAplicables.construirContenedor()