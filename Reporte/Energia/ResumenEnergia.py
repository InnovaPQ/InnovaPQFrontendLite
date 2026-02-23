import streamlit as st
from Modelos import Tabla


def ResumenEnergia(Servicio,Datos):


    with st.container():
        st.subheader("Resumen de mediciones")
        
        with st.expander(label="PotenciaDemandas"):
            rutaTablaDemandas=Datos["Potencia"]["PotenciaDemandas"]
            TablaResumenActiva=Tabla("Totales Demanda",rutaDatos=rutaTablaDemandas,servicio=Servicio)
            TablaResumenActiva.construirContenedor()

        with st.expander(label="PotenciaEnergia"):
            rutaTablaEnergia=Datos["Potencia"]["PotenciaEnergia"]
            TablaResumenReactiva=Tabla("Totales Energía",rutaDatos=rutaTablaEnergia,servicio=Servicio)
            TablaResumenReactiva.construirContenedor()
