import streamlit as st
from Modelos import Imagenes




def ActivaReactivaEnergia(Servicio,Datos):


    with st.container():
        
        with st.expander(label="Demanda Energía Activa"):

            rutaImagenDemandaActiva=Datos["Potencia"]["EnergiaActiva"]
            ImagenDemandaActiva=Imagenes("Energía Activa",rutaDatos=rutaImagenDemandaActiva,servicio=Servicio)
            ImagenDemandaActiva.ConstruirImagen()


        with st.expander(label="Demanda Energía Reactiva"):
            rutaImagenDeamandaReactiva=Datos["Potencia"]["EnergiaReactiva"]
            ImagenDemandaReactiva=Imagenes("Energía Reactiva",rutaDatos=rutaImagenDeamandaReactiva,servicio=Servicio)
            ImagenDemandaReactiva.ConstruirImagen()
