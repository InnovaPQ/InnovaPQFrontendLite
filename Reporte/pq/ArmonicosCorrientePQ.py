import streamlit as st
from Modelos import Tabla,Imagenes




def ArmonicosCorrientePQ(Servicio,Datos):

 

    with st.container():
            rutaTablaDescriptivasTHDCorriente=Datos["ArmonicosCorriente"]["ArmonicosITabla"]
            TablaDescriptivasTHDCorriente=Tabla("Descripción THD Corriente",rutaDatos=rutaTablaDescriptivasTHDCorriente,servicio=Servicio)
            TablaDescriptivasTHDCorriente.construirContenedor()
    with st.expander(label="Gráficas THD Corriente"):
        with st.container():
            rutaImagenTHDCorriente=Datos["ArmonicosCorriente"]["ArmonicosITiempo"]
            ImagenTHDCorriente=Imagenes("THD Corriente Serie de Tiempo",rutaDatos=rutaImagenTHDCorriente,servicio=Servicio)
            ImagenTHDCorriente.ConstruirImagen()
        with st.container():
            rutaImagenTHDCorrienteDistr=Datos["ArmonicosCorriente"]["ArmonicosIDistr"]
            ImagenTHDCorrienteDistr=Imagenes("THD Corriente Distribución",rutaDatos=rutaImagenTHDCorrienteDistr,servicio=Servicio)
            ImagenTHDCorrienteDistr.ConstruirImagen()
    with st.expander(label="THD Corriente por línea"):
        with st.container():
            rutaImagenTHDCorrienteDistrL1=Datos["ArmonicosCorriente"]["ArmonicosIL1"]
            ImagenTHDCorrienteDistrL1=Imagenes("THD Corriente L1",rutaDatos=rutaImagenTHDCorrienteDistrL1,servicio=Servicio)
            ImagenTHDCorrienteDistrL1.ConstruirImagen()
        with st.container():
            rutaImagenTHDCorrienteDistrL2=Datos["ArmonicosCorriente"]["ArmonicosIL2"]
            ImagenTHDCorrienteDistrL2=Imagenes("THD Corriente L2",rutaDatos=rutaImagenTHDCorrienteDistrL2,servicio=Servicio)
            ImagenTHDCorrienteDistrL2.ConstruirImagen()
        with st.container():
            rutaImagenTHDCorrienteDistrL3=Datos["ArmonicosCorriente"]["ArmonicosIL3"]
            ImagenTHDCorrienteDistrL3=Imagenes("THD Corriente L3",rutaDatos=rutaImagenTHDCorrienteDistrL3,servicio=Servicio)
            ImagenTHDCorrienteDistrL3.ConstruirImagen()
        