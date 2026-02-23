import streamlit as st
from Modelos import Tabla,Imagenes




def FactorKPQ(Servicio,Datos):

 

    with st.container():
            rutaTablaFKCuartil=Datos["FactorK"]["FKCuartil"]
            TablaFKCuartil=Tabla("Resumen Factor K",rutaDatos=rutaTablaFKCuartil,servicio=Servicio)
            TablaFKCuartil.construirContenedor()

    with st.expander(label="Resumen detallado del Factor K"):
            rutaTablaFKDescriptivo=Datos["FactorK"]["FKDescriptivo"]
            TablaFKDescriptivo=Tabla("Detalle Factor K",rutaDatos=rutaTablaFKDescriptivo,servicio=Servicio)
            TablaFKDescriptivo.construirContenedor()

    with st.expander(label="Gráficas Factor K"):
        with st.container():
            rutaImagenFKSerie=Datos["FactorK"]["FKSerie"]
            ImagenFKSerie=Imagenes("Factor K Serie de Tiempo",rutaDatos=rutaImagenFKSerie,servicio=Servicio)
            ImagenFKSerie.ConstruirImagen()
        with st.container():
            rutaImagenFKHistograma=Datos["FactorK"]["FKHistograma"]
            ImagenFKHistograma=Imagenes("Factor K Distribución",rutaDatos=rutaImagenFKHistograma,servicio=Servicio)
            ImagenFKHistograma.ConstruirImagen()
    
        