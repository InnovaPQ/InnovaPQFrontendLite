import streamlit as st
from Modelos import Imagenes




def FactoresEnergia(Servicio,Datos):


    with st.container():
        
        with st.expander(label="Factor de Potencia"):

            rutaImagenIndFactorPotencia=Datos["Potencia"]["IndicadorFP"]
            ImagenIndFactorPotenica=Imagenes("Factor de Potencia",rutaDatos=rutaImagenIndFactorPotencia,servicio=Servicio)
            ImagenIndFactorPotenica.ConstruirImagen()


        with st.expander(label="Factor de Carga"):
            rutaImagenIndFactorCarga=Datos["Potencia"]["IndicadorFC"]
            ImagenIndFactorCarga=Imagenes("Factor de Carga",rutaDatos=rutaImagenIndFactorCarga,servicio=Servicio)
            ImagenIndFactorCarga.ConstruirImagen()
