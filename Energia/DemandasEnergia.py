import streamlit as st
from Modelos import Imagenes




def DemandasEnergia(Servicio,Datos):


    with st.container():
        
        with st.expander(label="Perfil Diario"):

            rutaImagenPerfilDiario=Datos["Potencia"]["PerfilDiario"]
            ImagenPerfilDiario=Imagenes("Perfil diario de demanda",rutaDatos=rutaImagenPerfilDiario,servicio=Servicio)
            ImagenPerfilDiario.ConstruirImagen()


        with st.expander(label="Mapa de calor"):
            rutaImagenHeatmap=Datos["Potencia"]["Heatmap"]
            ImagenHeatmap=Imagenes("Mapa de calor",rutaDatos=rutaImagenHeatmap,servicio=Servicio)
            ImagenHeatmap.ConstruirImagen()
        
        with st.expander(label="Demanda 3D"):
            rutaImagenDemanda3D=Datos["Potencia"]["Demanda3D"]
            ImagenDemanda3D=Imagenes("Demanda 3D",rutaDatos=rutaImagenDemanda3D,servicio=Servicio)
            ImagenDemanda3D.ConstruirImagen()
