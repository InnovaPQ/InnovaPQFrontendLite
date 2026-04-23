import streamlit as st
from Modelos import Descripciones,Imagenes





def Descripcion(Servicio,Datos):

    with st.container():
        rutaCentroCarga=Datos["Contexto"]["Descripcion"]
        DescripcionCentroCarga=Descripciones(rutaDatos=rutaCentroCarga,servicio=Servicio)
        DescripcionCentroCarga.ConstruirContenedor()
    # --- Diagrama Unifilar---
    with st.container():
        st.subheader("Diagrama Unifilar")
        rutaUnifilar=Datos["Unifilar"]
        ImagenUnifilar=Imagenes("",rutaDatos=rutaUnifilar,servicio=Servicio)
        ImagenUnifilar.ConstruirImagen()
    # --- Información General ---
    with st.expander(label="Datos de medición"):
        rutaDatosMedicion=Datos["Contexto"]["Medicion"]
        DescripcionDatos=Descripciones(rutaDatos=rutaDatosMedicion,servicio=Servicio)
        DescripcionDatos.ConstruirContenedor()

    with st.expander(label="Datos del punto de medición"):
        rutaPuntoMedicion=Datos["Contexto"]["PuntoMedicion"]
        DescripcionPuntoMedicion=Descripciones(rutaDatos=rutaPuntoMedicion,servicio=Servicio)
        DescripcionPuntoMedicion.ConstruirContenedor()

    with st.expander(label="Información del centro de carga"):
        rutaInfoCarga=Datos["Contexto"]["Informacion"]
        DescripcionInfoCarga=Descripciones(rutaDatos=rutaInfoCarga,servicio=Servicio)
        DescripcionInfoCarga.ConstruirContenedor()

    with st.expander(label="Información del medidor"):
        rutaMedidor=Datos["Contexto"]["Medidor"]
        DescripcionMedidor=Descripciones(rutaDatos=rutaMedidor,servicio=Servicio)
        DescripcionMedidor.ConstruirContenedor()
