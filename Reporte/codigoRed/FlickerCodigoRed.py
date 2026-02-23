import streamlit as st
from Modelos import Tabla,Imagenes




def FlickerCodigoRed(Servicio,Datos):


    with st.container():
        st.subheader("Flicker")
        with st.container():
                with st.container():
                    rutaTablaDescriptivasFlicker=Datos["Flicker"]["FlickerTablaPst"]
                    TablaDescriptivasFlicker=Tabla("Descripción PST",rutaDatos=rutaTablaDescriptivasFlicker,servicio=Servicio)
                    TablaDescriptivasFlicker.construirContenedor()
                with st.container():
                    rutaTablaCumplimientoFlicker=Datos["Flicker"]["FlickerTablaPlt"]
                    TablaCumplimientoFlicker=Tabla("Descripción PLT",rutaDatos=rutaTablaCumplimientoFlicker,servicio=Servicio)
                    TablaCumplimientoFlicker.construirContenedor()

        with st.expander(label="PST"):
            with st.container():
                rutaImagenFlickerPst=Datos["Flicker"]["FlickerPstSerieTiempo"]
                ImagenFlickerPst=Imagenes("Flicker Pst Serie de Tiempo",rutaDatos=rutaImagenFlickerPst,servicio=Servicio)
                ImagenFlickerPst.ConstruirImagen()

            with st.container():
                rutaImagenFlickerPstDistr=Datos["Flicker"]["FlickerDistrPst"]
                ImagenFlickerPstDistr=Imagenes("Distribución Flicker Pst",rutaDatos=rutaImagenFlickerPstDistr,servicio=Servicio)
                ImagenFlickerPstDistr.ConstruirImagen()

        with st.expander(label="PLT"):
            
            with st.container():
                rutaImagenFlickerPlt=Datos["Flicker"]["FlickerPltSerieTiempo"]
                ImagenFlickerPlt=Imagenes("Flicker Plt Serie de Tiempo",rutaDatos=rutaImagenFlickerPlt,servicio=Servicio)
                ImagenFlickerPlt.ConstruirImagen()
            
            with st.container():
                rutaImagenFlickerPltDistr=Datos["Flicker"]["FlickerDistrPlt"]
                ImagenFlickerPltDistr=Imagenes("Distribución Flicker Plt",rutaDatos=rutaImagenFlickerPltDistr,servicio=Servicio)
                ImagenFlickerPltDistr.ConstruirImagen()   
            