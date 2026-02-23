import streamlit as st
from Modelos import Tabla,Imagenes




def FrecuenciaPQ(Servicio,Datos):
    


    with st.container():

        rutaTablaDescriptivasFrecuencia=Datos["Frecuencia"]["FrecuenciaTabla"]
        TablaDescriptivasFrecuencia=Tabla("Descripción Frecuencia",rutaDatos=rutaTablaDescriptivasFrecuencia,servicio=Servicio)
        TablaDescriptivasFrecuencia.construirContenedor()

        rutaImagenFrecuencia=Datos["Frecuencia"]["FrecuenciaSerieTiempo"]
        ImagenFrecuencia=Imagenes("Frecuencia Serie de Tiempo",rutaDatos=rutaImagenFrecuencia,servicio=Servicio)
        ImagenFrecuencia.ConstruirImagen()

        rutaImagenFrecuenciaDistr=Datos["Frecuencia"]["FrecuenciaDistr"]
        ImagenFrecuenciaDistr=Imagenes("Distribución de Frecuencia",rutaDatos=rutaImagenFrecuenciaDistr,servicio=Servicio)
        ImagenFrecuenciaDistr.ConstruirImagen()

            