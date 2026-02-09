import streamlit as st
from Modelos import Tabla,Imagenes



def DesbalancesPQ(Servicio,Datos):


    with st.container():
        with st.container():
            with st.container():
                rutaTablaDescriptivasDesbalanceV=Datos["Desbalance"]["DesbalanceTablaDescriptivaVoltaje"]
                TablaDescriptivasDesbalanceV=Tabla("Descripción Desbalances Voltaje",rutaDatos=rutaTablaDescriptivasDesbalanceV,servicio=Servicio)
                TablaDescriptivasDesbalanceV.construirContenedor()
            with st.container():
                rutaTablaDescriptivasDesbalanceC=Datos["Desbalance"]["DesbalanceTablaDescriptivaCorriente"]
                TablaDescriptivasDesbalanceC=Tabla("Descripción Desbalances Corriente",rutaDatos=rutaTablaDescriptivasDesbalanceC,servicio=Servicio)
                TablaDescriptivasDesbalanceC.construirContenedor()

        with st.expander(label="Desbalance Voltajes"):
            with st.container():
                rutaImagenDesbalanceVoltaje=Datos["Desbalance"]["DesbalanceVoltajeSerieTiempo"]
                ImagenDesbalanceVoltaje=Imagenes("Desbalance de Voltaje",rutaDatos=rutaImagenDesbalanceVoltaje,servicio=Servicio)
                ImagenDesbalanceVoltaje.ConstruirImagen()
            with st.container():
                rutaDesbalanceDistrVoltaje=Datos["Desbalance"]["DesbalanceDistrVoltaje"]
                ImagenDesbalanceDistrVoltaje=Imagenes("Distribución Desbalance de Voltaje",rutaDatos=rutaDesbalanceDistrVoltaje,servicio=Servicio)
                ImagenDesbalanceDistrVoltaje.ConstruirImagen()
            
        with st.expander(label="Desbalance Corrientes"):

            with st.container():
                rutaImagenDesbalanceCorriente=Datos["Desbalance"]["DesbalanceCorrienteSerieTiempo"]
                ImagenDesbalanceCorriente=Imagenes("Desbalance de Corriente",rutaDatos=rutaImagenDesbalanceCorriente,servicio=Servicio)
                ImagenDesbalanceCorriente.ConstruirImagen()
            
            with st.container():
                rutaDesbalanceDistrCorriente=Datos["Desbalance"]["DesbalanceDistrCorriente"]
                ImagenDesbalanceDistrCorriente=Imagenes("Distribución Desbalance de Corriente",rutaDatos=rutaDesbalanceDistrCorriente,servicio=Servicio)
                ImagenDesbalanceDistrCorriente.ConstruirImagen()
            