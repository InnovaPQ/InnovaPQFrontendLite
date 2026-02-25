import streamlit as st
from Modelos import Comentarios
from Servicio import Data
from Reporte.Energia.DescripcionEEnergia import Descripcion
from Reporte.Energia.ResumenEnergia import ResumenEnergia
from Reporte.Energia.FactoresEnergia import FactoresEnergia
from Reporte.Energia.ActivaReactivaEnergia import ActivaReactivaEnergia
from Reporte.Energia.DemandasEnergia import DemandasEnergia
from Reporte.Energia.cfe import CFE


def Ventana(MostrarVista,Servicio,Datos,cfe):
    match MostrarVista:
        case "Descripcion":
            return Descripcion(Servicio,Datos)
        case "Resumen":
            return ResumenEnergia(Servicio,Datos)
        case "Factores":
            return FactoresEnergia(Servicio,Datos)
        case "Energia":
            return ActivaReactivaEnergia(Servicio,Datos)
        case "Demandas":
            return DemandasEnergia(Servicio,Datos)
        case "cfe":
            return CFE(Servicio,Datos,cfe)




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





   
def Energia(report_id,cfe):

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
        "Resumen",
        "Factores Potencia y Carga",
        "Energía Activa y Reactiva",
        "Demandas",
        "CFE"
    
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
        "Resumen":"Resumen",
        "Factores Potencia y Carga":"Factores",
        "Energía Activa y Reactiva":"Energia",
        "Demandas":"Demandas",
        "CFE":"cfe"
   
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
                key=f"tab_btn_{idx}_Energia",
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
                    key=f"tab_btn_{mitad + idx}_Energia",
                    use_container_width=True,
                    type=button_type
                ):
                    st.session_state.mostrar_vista = opcion
                    st.rerun()
    
    st.divider()
    
    # Renderizar el contenido abajo basado en la vista seleccionada
    # Convertir el nombre de UI al nombre interno usando el mapeo
    vista_interna = mapeo_vistas.get(st.session_state.mostrar_vista, st.session_state.mostrar_vista)
    Ventana(MostrarVista=vista_interna, Servicio=Servicio, Datos=Datos,cfe=cfe)

    # Sidebar para comentarios (Notas, Importante, Precaución)
    with st.sidebar:
        st.markdown("# Comentarios Reporte Energía")
        
        rutaComentarios=Datos["Comentarios"]["Energia"]
        
        # Inicializar clave para el JSON completo
        json_key = f"comentarios_json_{rutaComentarios}"

        SeccionNotas=Comentarios(titulo="Notas",seccion_json="nota",rutaDatos=rutaComentarios,servicio=Servicio,id_categoria="Energia")
        json_actualizado = SeccionNotas.render()

        SeccionImportante=Comentarios(titulo="Importante",seccion_json="importante",rutaDatos=rutaComentarios,servicio=Servicio,id_categoria="Energia")
        json_actualizado = SeccionImportante.render()

        SeccionPrecaucion=Comentarios(titulo="Precaución",seccion_json="precaucion",rutaDatos=rutaComentarios,servicio=Servicio,id_categoria="Energia")
        json_actualizado = SeccionPrecaucion.render()
        
        # Obtener el JSON completo actualizado del session_state
        if json_key in st.session_state:
            json_completo_final = st.session_state[json_key]
        else:
            json_completo_final = json_actualizado
        
        st.divider()
        
 