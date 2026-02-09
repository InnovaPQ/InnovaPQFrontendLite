import streamlit as st
from Modelos import Tabla,Imagenes



def ArmonicosVoltajePQ(Servicio,Datos):



    with st.container():
        rutaTablaDescriptivasTHDVoltaje=Datos["ArmonicosVoltaje"]["ArmonicosTabla"]
        TablaDescriptivasTHDVoltaje=Tabla("Descripción Armónicos Voltaje",rutaDatos=rutaTablaDescriptivasTHDVoltaje,servicio=Servicio)
        TablaDescriptivasTHDVoltaje.construirContenedor()

    with st.expander(label="Gráficas THD Voltaje"):
        
        with st.container():
            rutaImagenTHDVoltaje=Datos["ArmonicosVoltaje"]["ArmonicosTiempo"]
            ImagenTHDVoltaje=Imagenes("THD Voltaje Serie de Tiempo",rutaDatos=rutaImagenTHDVoltaje,servicio=Servicio)
            ImagenTHDVoltaje.ConstruirImagen()

        with st.container():
            rutaImagenTHDVoltajeDistr=Datos["ArmonicosVoltaje"]["ArmonicosDistr"]
            ImagenTHDVoltajeDistr=Imagenes("THD Voltaje Distribución",rutaDatos=rutaImagenTHDVoltajeDistr,servicio=Servicio)
            ImagenTHDVoltajeDistr.ConstruirImagen()

    with st.expander(label="THD Voltaje por línea"):
        with st.container():
            rutaImagenTHDVoltajeDistrL1=Datos["ArmonicosVoltaje"]["ArmonicosL1"]
            ImagenTHDVoltajeDistrL1=Imagenes("THD Voltaje L1",rutaDatos=rutaImagenTHDVoltajeDistrL1,servicio=Servicio)
            ImagenTHDVoltajeDistrL1.ConstruirImagen()
        with st.container():
            rutaImagenTHDVoltajeDistrL2=Datos["ArmonicosVoltaje"]["ArmonicosL2"]
            ImagenTHDVoltajeDistrL2=Imagenes("THD Voltaje L2",rutaDatos=rutaImagenTHDVoltajeDistrL2,servicio=Servicio)
            ImagenTHDVoltajeDistrL2.ConstruirImagen()
        with st.container():
            rutaImagenTHDVoltajeDistrL3=Datos["ArmonicosVoltaje"]["ArmonicosL3"]
            ImagenTHDVoltajeDistrL3=Imagenes("THD Voltaje L3",rutaDatos=rutaImagenTHDVoltajeDistrL3,servicio=Servicio)
            ImagenTHDVoltajeDistrL3.ConstruirImagen()
        