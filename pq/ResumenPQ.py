import streamlit as st
from Modelos import Tabla


def ResumenPQ(Servicio,Datos):


    with st.container():
        st.subheader("Resumen de mediciones")

        with st.container():
            rutaTablaResumenRapido=Datos["CumplimientoRed"]["ResumenRapido"]
            TablaResumenRapido=Tabla("Resumen rápido IEEE",rutaDatos=rutaTablaResumenRapido,servicio=Servicio)
            TablaResumenRapido.construirContenedor()
        
        with st.expander(label="Potencia activa"):
            rutaTablaResumenActiva=Datos["Resumen"]["ResumenActiva"]
            TablaResumenActiva=Tabla("Potencia activa",rutaDatos=rutaTablaResumenActiva,servicio=Servicio)
            TablaResumenActiva.construirContenedor()

        with st.expander(label="Potencia reactiva"):
            rutaTablaReactiva=Datos["Resumen"]["ResumenReactiva"]
            TablaResumenReactiva=Tabla("Potencia reactiva",rutaDatos=rutaTablaReactiva,servicio=Servicio)
            TablaResumenReactiva.construirContenedor()

        with st.expander(label="Potencia aparente"):
            rutaTablaAparente=Datos["Resumen"]["ResumenAparente"]
            TablaResumenAparente=Tabla("Potencia aparente",rutaDatos=rutaTablaAparente,servicio=Servicio)
            TablaResumenAparente.construirContenedor()

        with st.expander(label="Factor de potencia"):
            rutaTablaFP=Datos["Resumen"]["ResumenFP"]
            TablaResumenFP=Tabla("Factor de potencia",rutaDatos=rutaTablaFP,servicio=Servicio)
            TablaResumenFP.construirContenedor()

        with st.expander(label="THD"):
            rutaTablaTHD=Datos["Resumen"]["ResumenTHD"]
            TablaResumenTHD=Tabla("THD",rutaDatos=rutaTablaTHD,servicio=Servicio)
            TablaResumenTHD.construirContenedor()

        with st.expander(label="TDD"):
            rutaTablaTDD=Datos["Resumen"]["ResumenTDD"]
            TablaResumenTDD=Tabla("TDD",rutaDatos=rutaTablaTDD,servicio=Servicio)
            TablaResumenTDD.construirContenedor()

        with st.expander(label="Desbalance de voltaje"):
            rutaTablaDesVoltaje=Datos["Resumen"]["ResumenDesVoltaje"]
            TablaResumenDesVoltaje=Tabla("Desbalance de voltaje",rutaDatos=rutaTablaDesVoltaje,servicio=Servicio)
            TablaResumenDesVoltaje.construirContenedor()

        with st.expander(label="Desbalance de corriente"):
            rutaTablaDesCorriente=Datos["Resumen"]["ResumenDesCorriente"]
            TablaResumenDesCorriente=Tabla("Desbalance de corriente",rutaDatos=rutaTablaDesCorriente,servicio=Servicio)
            TablaResumenDesCorriente.construirContenedor()

        with st.expander(label="Voltajes RMS"):
            rutaTablaVProm=Datos["Resumen"]["ResumenVProm"]
            TablaResumenVProm=Tabla("Voltajes RMS",rutaDatos=rutaTablaVProm,servicio=Servicio)
            TablaResumenVProm.construirContenedor()

        with st.expander(label="Corrientes RMS"):
            rutaTablaCProm=Datos["Resumen"]["ResumenCProm"]
            TablaResumenCProm=Tabla("Corrientes RMS",rutaDatos=rutaTablaCProm,servicio=Servicio)
            TablaResumenCProm.construirContenedor()

        with st.expander(label="Flicker Pst"):
            rutaTablaFlickPst=Datos["Resumen"]["ResumenFlickPst"]
            TablaResumenFlickPst=Tabla("Flicker Pst",rutaDatos=rutaTablaFlickPst,servicio=Servicio)
            TablaResumenFlickPst.construirContenedor()

        with st.expander(label="Flicker Plt"):
            rutaTablaFlickPlt=Datos["Resumen"]["ResumenFlickPlt"]
            TablaResumenFlickPlt=Tabla("Flicker Plt",rutaDatos=rutaTablaFlickPlt,servicio=Servicio)
            TablaResumenFlickPlt.construirContenedor()

        with st.expander(label="Frecuencia"):
            rutaTablaFrecuencia=Datos["Resumen"]["ResumenFrecuencia"]
            TablaResumenFrecuencia=Tabla("Frecuencia",rutaDatos=rutaTablaFrecuencia,servicio=Servicio)
            TablaResumenFrecuencia.construirContenedor()
