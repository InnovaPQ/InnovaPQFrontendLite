import streamlit as st
from Modelos import Imagenes


def ITIC(Servicio, Datos, itic):

    if itic == "true":

        with st.container():

            with st.expander(label="Curva ITIC / CBEMA"):
                rutaCurvaITIC = Datos["ITIC"]["CurvaITIC"]
                ImagenCurvaITIC = Imagenes("Curva ITIC", rutaDatos=rutaCurvaITIC, servicio=Servicio)
                ImagenCurvaITIC.ConstruirImagen()

    else:
        st.warning("⚠️ Este cliente no se procesó con archivo de eventos de la Curva ITIC.")
