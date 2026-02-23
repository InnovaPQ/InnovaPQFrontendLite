import streamlit as st
from Modelos import Tabla,Imagenes




def CorrientesCodigoRed(Servicio,Datos):

    with st.container():
            rutaTablaDescriptivasCorriente=Datos["Corriente"]["CorrienteTablaDescriptiva"]
            TablaDescriptivasCorriente=Tabla("Descripción Corrientes RMS",rutaDatos=rutaTablaDescriptivasCorriente,servicio=Servicio)
            TablaDescriptivasCorriente.construirContenedor()
    with st.expander(label="Corrientes RMS"):
        with st.container():
            rutaImagenCorrienteRMSMaximo=Datos["Corriente"]["CorrienteRMSMaximo"]
            ImagenCorrienteRMSMaximo=Imagenes("Corrientes RMS Máximo",rutaDatos=rutaImagenCorrienteRMSMaximo,servicio=Servicio)
            ImagenCorrienteRMSMaximo.ConstruirImagen()
        with st.container():
            rutaImagenCorrienteRMSMinimo=Datos["Corriente"]["CorrienteRMSMinimo"]
            ImagenCorrienteRMSMinimo=Imagenes("Corrientes RMS Mínimo",rutaDatos=rutaImagenCorrienteRMSMinimo,servicio=Servicio)
            ImagenCorrienteRMSMinimo.ConstruirImagen()
            
        with st.container():
            rutaImagenCorrienteRMSPromedio=Datos["Corriente"]["CorrienteRMSPromedio"]
            ImagenCorrienteRMSPromedio=Imagenes("Corrientes RMS Promedio",rutaDatos=rutaImagenCorrienteRMSPromedio,servicio=Servicio)
            ImagenCorrienteRMSPromedio.ConstruirImagen()

    with st.expander(label="Distribución de corrientes"):

        rutaImagenDistribucionCorriente=Datos["Corriente"]["CorrienteDistr"]
        ImagenDistribucionCorriente=Imagenes("Distribución Corrientes",rutaDatos=rutaImagenDistribucionCorriente,servicio=Servicio)
        ImagenDistribucionCorriente.ConstruirImagen()
        