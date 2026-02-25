import streamlit as st
from Modelos import Imagenes




def CFE(Servicio,Datos,cfe):

    if cfe=="true":

        with st.container():
            
            with st.expander(label="Desglose de Importes Anuales"):

                rutaImagenDemandaActiva=Datos["CFE"]["ImportesAnuales"]
                ImagenDemandaActiva=Imagenes("Importes Anuales",rutaDatos=rutaImagenDemandaActiva,servicio=Servicio)
                ImagenDemandaActiva.ConstruirImagen()


            with st.expander(label="Desglose de Porcentajes Conceptos"):
                rutaImagenDeamandaReactiva=Datos["CFE"]["PorcentajesConceptos"]
                ImagenDemandaReactiva=Imagenes("Porcentajes Conceptos",rutaDatos=rutaImagenDeamandaReactiva,servicio=Servicio)
                ImagenDemandaReactiva.ConstruirImagen()

            with st.expander(label="Costo de Facturación Mensual"):
                rutaImagenDeamandaReactiva=Datos["CFE"]["CostoFacturacion"]
                ImagenDemandaReactiva=Imagenes("Costo de Facturación",rutaDatos=rutaImagenDeamandaReactiva,servicio=Servicio)
                ImagenDemandaReactiva.ConstruirImagen()

            with st.expander(label="Demanda Mensual por Bloque"):
                rutaImagenDeamandaReactiva=Datos["CFE"]["DemandaBloqueHorario"]
                ImagenDemandaReactiva=Imagenes("Demanda Mensual",rutaDatos=rutaImagenDeamandaReactiva,servicio=Servicio)
                ImagenDemandaReactiva.ConstruirImagen()

            with st.expander(label="Demanda Cargo por Capacidad Mensual"):
                rutaImagenDeamandaReactiva=Datos["CFE"]["CargoCapacidad"]
                ImagenDemandaReactiva=Imagenes("Cargo por Capacidad",rutaDatos=rutaImagenDeamandaReactiva,servicio=Servicio)
                ImagenDemandaReactiva.ConstruirImagen()

            with st.expander(label="Demanda Cargo por Distribución Mensual"):
                rutaImagenDeamandaReactiva=Datos["CFE"]["CargoDistribucion"]
                ImagenDemandaReactiva=Imagenes("Cargo por Distribución",rutaDatos=rutaImagenDeamandaReactiva,servicio=Servicio)
                ImagenDemandaReactiva.ConstruirImagen()

            with st.expander(label="Desglose de Cargos de Facturación Mensual"):
                rutaImagenDeamandaReactiva=Datos["CFE"]["CargosFacturacion"]
                ImagenDemandaReactiva=Imagenes("Cargos por Facturación",rutaDatos=rutaImagenDeamandaReactiva,servicio=Servicio)
                ImagenDemandaReactiva.ConstruirImagen()

            with st.expander(label="Consumo Mensual Energía Activa"):
                rutaImagenDeamandaReactiva=Datos["CFE"]["EnergiaBloqueHorario"]
                ImagenDemandaReactiva=Imagenes("Energía Activa",rutaDatos=rutaImagenDeamandaReactiva,servicio=Servicio)
                ImagenDemandaReactiva.ConstruirImagen()

            with st.expander(label="Consumo Mensual Energía Reactiva"):
                rutaImagenDeamandaReactiva=Datos["CFE"]["ReactivaTotal"]
                ImagenDemandaReactiva=Imagenes("Energía Reactiva",rutaDatos=rutaImagenDeamandaReactiva,servicio=Servicio)
                ImagenDemandaReactiva.ConstruirImagen()

            with st.expander(label="Consumo Mensual Energía Total"):
                rutaImagenDeamandaReactiva=Datos["CFE"]["EnergiaTotal"]
                ImagenDemandaReactiva=Imagenes("Energía Total",rutaDatos=rutaImagenDeamandaReactiva,servicio=Servicio)
                ImagenDemandaReactiva.ConstruirImagen()

            with st.expander(label="Factor de Carga"):
                rutaImagenDeamandaReactiva=Datos["CFE"]["FactorCarga"]
                ImagenDemandaReactiva=Imagenes("Factor de Carga",rutaDatos=rutaImagenDeamandaReactiva,servicio=Servicio)
                ImagenDemandaReactiva.ConstruirImagen()

            with st.expander(label="Factor de Potencia"):
                rutaImagenDeamandaReactiva=Datos["CFE"]["FactorPotencia"]
                ImagenDemandaReactiva=Imagenes("Factor de Potencia",rutaDatos=rutaImagenDeamandaReactiva,servicio=Servicio)
                ImagenDemandaReactiva.ConstruirImagen()
            
            with st.expander(label="Tarifa Integrada All In Mensual"):
                rutaImagenDeamandaReactiva=Datos["CFE"]["TarifaAllIn"]
                ImagenDemandaReactiva=Imagenes("Tarifa All In",rutaDatos=rutaImagenDeamandaReactiva,servicio=Servicio)
                ImagenDemandaReactiva.ConstruirImagen()


            
    else:
        st.warning("⚠️ Este cliente no se procesó con el archivo de la Comisión Federal de Electricidad.")