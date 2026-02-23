import streamlit as st
from Modelos import Tabla,Imagenes





def VoltajesPQ(Servicio,Datos):


    with st.container():

        with st.container():
            rutaTablaDescriptivasVoltaje=Datos["Voltaje"]["VoltajeTablaDescriptiva"]
            TablaDescriptivasVoltaje=Tabla("Descripción Voltajes RMS L-L",rutaDatos=rutaTablaDescriptivasVoltaje,servicio=Servicio)
            TablaDescriptivasVoltaje.construirContenedor()

        with st.expander(label="Voltajes RMS L-L"):
            rutaImagenVoltajeRMSMaximo=Datos["Voltaje"]["VoltajeRMSMaximo"]
            ImagenVoltajeRMSMaximo=Imagenes("Voltajes RMS Máximo",rutaDatos=rutaImagenVoltajeRMSMaximo,servicio=Servicio)
            ImagenVoltajeRMSMaximo.ConstruirImagen()

            rutaImagenVoltajeRMSMinimo=Datos["Voltaje"]["VoltajeRMSMinimo"]
            ImagenVoltajeRMSMinimo=Imagenes("Voltajes RMS Mínimo",rutaDatos=rutaImagenVoltajeRMSMinimo,servicio=Servicio)
            ImagenVoltajeRMSMinimo.ConstruirImagen()

            rutaImagenVoltajeRMSPromedio=Datos["Voltaje"]["VoltajeRMSPromedio"]
            ImagenVoltajeRMSPromedio=Imagenes("Voltajes RMS Promedio",rutaDatos=rutaImagenVoltajeRMSPromedio,servicio=Servicio)
            ImagenVoltajeRMSPromedio.ConstruirImagen()

        with st.expander(label="Distribución Voltaje L-L"):
            rutaImagenDistribucionLL=Datos["Voltaje"]["VoltajeDistrLL"]
            ImagenDistribucionLL=Imagenes("Distribución Voltaje L-L",rutaDatos=rutaImagenDistribucionLL,servicio=Servicio)
            ImagenDistribucionLL.ConstruirImagen()
        