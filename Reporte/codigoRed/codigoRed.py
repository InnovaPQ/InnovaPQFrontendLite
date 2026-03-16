import streamlit as st
from Modelos import Comentarios
from Servicio import Data
from Reporte.codigoRed.DescripcionCodigoRed import Descripcion
from Reporte.codigoRed.CumplimientoCodigoRed import Cumplimiento
from Reporte.codigoRed.ResumenCodigoRed import ResumenCodigoRed
from Reporte.codigoRed.PotenciaCodigoRed import PotenciaCodigoRed
from Reporte.codigoRed.VoltajesCodigoRed import VoltajesCodigoRed
from Reporte.codigoRed.CorrientesCodigoRed import CorrientesCodigoRed
from Reporte.codigoRed.DesbalancesCodigoRed import DesbalancesCodigoRed
from Reporte.codigoRed.FrecuenciaCodigoRed import FrecuenciaCodigoRed
from Reporte.codigoRed.FlickerCodigoRed import FlickerCodigoRed
from Reporte.codigoRed.ArmonicosVoltajeCodigoRed import ArmonicosVoltaje
from Reporte.codigoRed.ArmonicosCorrienteCodigoRed import ArmonicosCorriente

def Ventana(MostrarVista,Servicio,Datos):
    match MostrarVista:
        case "Descripcion":
            return Descripcion(Servicio,Datos)
        case "Cumplimiento":
            return Cumplimiento(Servicio,Datos)
        case "Resumen Sistema":
            return ResumenCodigoRed(Servicio,Datos)
        case "Potencia":
            return PotenciaCodigoRed(Servicio,Datos)
        case "Voltajes":
            return VoltajesCodigoRed(Servicio,Datos)
        case "Corrientes":
            return CorrientesCodigoRed(Servicio,Datos)
        case "Desbalances":
            return DesbalancesCodigoRed(Servicio,Datos)
        case "Frecuencia":
            return FrecuenciaCodigoRed(Servicio,Datos)
        case "Flicker":
            return FlickerCodigoRed(Servicio,Datos)
        case "Armonicos Voltaje":
            return ArmonicosVoltaje(Servicio,Datos)
        case "Armonicos Corriente":
            return ArmonicosCorriente(Servicio,Datos)
        

@st.cache_resource
def get_servicio_aws(report_id, _version=1):
    """
    Obtiene la instancia del servicio AWS.
    _version se usa para invalidar el caché cuando cambia el código.
    """
    print("Conectando a AWS...")
    return Data(report_id)

@st.cache_data
def get_diccionario_rutas(_Servicio,nombre_carpeta):
    print("Escaneando bucket...")
    return _Servicio.obtener_rutas_actualizadas()





   
def CodigoRed(report_id):

    Servicio=get_servicio_aws(report_id, _version=1)
    Datos=get_diccionario_rutas(_Servicio=Servicio,nombre_carpeta=report_id)
# --- Lógica Principal de la Aplicación ---
    if 'mostrar_vista' not in st.session_state:
        st.session_state.mostrar_vista = "Descripcion"

    def MostrarVistaFunc(Pagina):
        st.session_state.mostrar_vista=Pagina
        return st.session_state.mostrar_vista

    # Header más pequeño
    st.caption(f'ID: {report_id}')
    
    # Selector de secciones como tabs horizontales (arriba)
    opciones_vista = [
        "Descripción",
        "Cumplimiento", 
        "Resumen Sistema",
        "Potencia",
        "Voltajes",
        "Corrientes",
        "Desbalances",
        "Frecuencia",
        "Flicker",
        "Armonicos Voltaje",
        "Armonicos Corriente"
    ]
    
    # Obtener el índice de la vista actual
    try:
        indice_actual = opciones_vista.index(st.session_state.mostrar_vista)
    except ValueError:
        indice_actual = 0
        st.session_state.mostrar_vista = opciones_vista[0]
    
    # Mapeo de nombres de UI a nombres internos
    mapeo_vistas = {
        "Descripción": "Descripcion",
        "Cumplimiento": "Cumplimiento",
        "Resumen Sistema": "Resumen Sistema",
        "Potencia": "Potencia",
        "Voltajes": "Voltajes",
        "Corrientes": "Corrientes",
        "Desbalances": "Desbalances",
        "Frecuencia": "Frecuencia",
        "Flicker": "Flicker",
        "Armonicos Voltaje": "Armonicos Voltaje",
        "Armonicos Corriente": "Armonicos Corriente"
    }
    
    # Usar botones en dos filas que funcionan como tabs
    # Agregar CSS para reducir el tamaño de fuente de los botones
    st.markdown("""
        <style>
            div[data-testid="stButton"] > button[kind="primary"],
            div[data-testid="stButton"] > button[kind="secondary"] {
                font-size: 0.7rem !important;
                padding: 0.3rem 0.4rem !important;
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Dividir los botones en dos filas
    num_botones = len(opciones_vista)
    mitad = (num_botones + 1) // 2  # Dividir en dos filas (primera fila puede tener uno más)
    
    # Primera fila
    primera_fila = opciones_vista[:mitad]
    segunda_fila = opciones_vista[mitad:]
    
    cols_fila1 = st.columns(len(primera_fila))
    for idx, col in enumerate(cols_fila1):
        with col:
            opcion = primera_fila[idx]
            button_type = "primary" if opcion == st.session_state.mostrar_vista else "secondary"
            
            if st.button(
                opcion,
                key=f"tab_btn_{idx}",
                use_container_width=True,
                type=button_type
            ):
                st.session_state.mostrar_vista = opcion
                st.rerun()
    
    # Segunda fila
    if segunda_fila:
        cols_fila2 = st.columns(len(segunda_fila))
        for idx, col in enumerate(cols_fila2):
            with col:
                opcion = segunda_fila[idx]
                button_type = "primary" if opcion == st.session_state.mostrar_vista else "secondary"
                
                if st.button(
                    opcion,
                    key=f"tab_btn_{mitad + idx}",
                    use_container_width=True,
                    type=button_type
                ):
                    st.session_state.mostrar_vista = opcion
                    st.rerun()
    
    st.divider()
    
    # Renderizar el contenido abajo basado en la vista seleccionada
    # Convertir el nombre de UI al nombre interno usando el mapeo
    vista_interna = mapeo_vistas.get(st.session_state.mostrar_vista, st.session_state.mostrar_vista)
    Ventana(MostrarVista=vista_interna, Servicio=Servicio, Datos=Datos)

    # Sidebar para comentarios (Notas, Importante, Precaución) de código red
    with st.sidebar:
        st.markdown("# Comentarios Reporte Codigo Red")
        
        rutaComentarios = Datos["Comentarios"]["CodigoRed"]
        
        # 1. Renderizamos las secciones directamente. 
        # La clase ya se encarga de guardar todo en st.session_state por debajo.
        Comentarios(
            titulo="Notas",
            seccion_json="nota",
            rutaDatos=rutaComentarios,
            servicio=Servicio,
            id_categoria="CodigoRed"
        ).render()

        Comentarios(
            titulo="Importante",
            seccion_json="importante",
            rutaDatos=rutaComentarios,
            servicio=Servicio,
            id_categoria="CodigoRed"
        ).render()

        Comentarios(
            titulo="Precaución",
            seccion_json="precaucion",
            rutaDatos=rutaComentarios,
            servicio=Servicio,
            id_categoria="CodigoRed"
        ).render()
        
        st.divider()
        
        # 2. (Opcional) Un pequeño indicador visual de que la memoria está activa
        json_key = f"comentarios_json_{rutaComentarios}"
        if json_key in st.session_state:
            st.caption("💾 Comentarios en memoria temporal")
        
        
    # El contenido ya se renderiza dentro de las tabs arriba
    # No necesitamos renderizarlo de nuevo aquí

                


            
        # En una v2, estos valores por defecto vendrían de un .txt o .json en S3
        #st.subheader("Notas")
        #comentario_Notas = st.text_area(label="",value="El voltaje se mantiene...")
        #st.subheader("Tips")
        #comentario_Tips = st.text_area(label="",value="Se detectaron picos de armónicos...")
        #st.subheader("Importante")
        #comentario_Importante = st.text_area(label="",value= "Se recomienda la instalación de...")
        #st.subheader("Precacución")
        #comentario_Precaucion = st.text_area(label="",value= "Cuidado con...")
        #st.subheader("Advertencia")
        #comentario_Advertencia = st.text_area(label="",value= "Accion inmediata")

        # --- 3. Generar PDF ---
        #st.header("Generar PDF")
            
        