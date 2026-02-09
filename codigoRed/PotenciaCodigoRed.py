import streamlit as st
from Modelos import Tabla,Imagenes




def PotenciaCodigoRed(Servicio,Datos):


    with st.container():
        

        with st.container():
            rutaTablaDescriptivasPotencia=Datos["Potencia"]["PotenciaDescriptivas"]
            TablaDescriptivasPotencia=Tabla("Descripción Potencia",rutaDatos=rutaTablaDescriptivasPotencia,servicio=Servicio)
            TablaDescriptivasPotencia.construirContenedor()

        with st.expander(label="Potencia Activa"):
            rutaImagenPotenciaActiva=Datos["Potencia"]["PotenciaActiva"]
            ImagenPotenciaActiva=Imagenes("Potencia Activa",rutaDatos=rutaImagenPotenciaActiva,servicio=Servicio)
            ImagenPotenciaActiva.ConstruirImagen()

            rutaImagenDistribucionActiva=Datos["Potencia"]["PotenciaDistribucionActiva"]
            ImagenDistribucionActiva=Imagenes("Distribución Potencia Activa",rutaDatos=rutaImagenDistribucionActiva,servicio=Servicio)
            ImagenDistribucionActiva.ConstruirImagen()
        
            

        with st.expander(label="Potencia Reactiva"):
            rutaImagenPotenciaReactiva=Datos["Potencia"]["PotenciaReactiva"]
            ImagenPotenciaReactiva=Imagenes("Potencia Reactiva",rutaDatos=rutaImagenPotenciaReactiva,servicio=Servicio)
            ImagenPotenciaReactiva.ConstruirImagen()

            rutaImagenDistribucionReactiva=Datos["Potencia"]["PotenciaDistribucionReactiva"]
            ImagenDistribucionReactiva=Imagenes("Distribución Potencia Reactiva",rutaDatos=rutaImagenDistribucionReactiva,servicio=Servicio)
            ImagenDistribucionReactiva.ConstruirImagen()
            

        with st.expander(label="Potencia Aparente"):
            rutaImagenPotenciaAparente=Datos["Potencia"]["PotenciaAparente"]
            ImagenPotenciaAparente=Imagenes("Potencia Aparente",rutaDatos=rutaImagenPotenciaAparente,servicio=Servicio)
            ImagenPotenciaAparente.ConstruirImagen()

            rutaImagenDistribucionAparente=Datos["Potencia"]["PotenciaDistribucionAparente"]
            ImagenDistribucionAparente=Imagenes("Distribución Potencia Aparente",rutaDatos=rutaImagenDistribucionAparente,servicio=Servicio)
            ImagenDistribucionAparente.ConstruirImagen()


        with st.expander(label="Factor de Potencia"):
            rutaImagenFactorPotencia=Datos["Potencia"]["PotenciaFp"]
            ImagenFactorPotencia=Imagenes("Factor de Potencia",rutaDatos=rutaImagenFactorPotencia,servicio=Servicio)
            ImagenFactorPotencia.ConstruirImagen()

            rutaImagenDistribucionFp=Datos["Potencia"]["PotenciaDistribucionFp"]
            ImagenDistribucionFp=Imagenes("Distribución Factor de Potencia",rutaDatos=rutaImagenDistribucionFp,servicio=Servicio)
            ImagenDistribucionFp.ConstruirImagen()
            