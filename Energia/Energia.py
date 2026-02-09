import streamlit as st
from Modelos import Comentarios
from Servicio import Data
from Energia.DescripcionEEnergia import Descripcion
from Energia.ResumenEnergia import ResumenEnergia
from Energia.FactoresEnergia import FactoresEnergia
from Energia.ActivaReactivaEnergia import ActivaReactivaEnergia
from Energia.DemandasEnergia import DemandasEnergia


def Ventana(MostrarVista,Servicio,Datos):
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





   
def Energia(report_id):

    Servicio=get_servicio_aws(report_id, _version=1)
    Datos=get_diccionario_rutas(_Servicio=Servicio,nombre_carpeta=report_id)
# --- Lógica Principal de la Aplicación ---
    if 'mostrar_vista' not in st.session_state:
        st.session_state.mostrar_vista = "Descripcion"

    def MostrarVistaFunc(Pagina):
        st.session_state.mostrar_vista=Pagina
        return st.session_state.mostrar_vista

    # Header más pequeño
    st.markdown("### Energía")
    st.caption(f'ID: {report_id}')
    
    # Selector de secciones como tabs horizontales (arriba)
    opciones_vista = [
        "Descripción",
        "Resumen",
        "Factores Potencia y Carga",
        "Energía Activa y Reactiva",
        "Demandas"
    
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
        "Demandas":"Demandas"
   
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

    # Sidebar para comentarios (Notas, Importante, Precaución)
    with st.sidebar:
        st.markdown("### Comentarios")
        st.divider()
        
        rutaComentarios=Datos["Comentarios"]["Energia"]
        
        # Inicializar clave para el JSON completo
        json_key = f"comentarios_json_{rutaComentarios}"

        SeccionNotas=Comentarios(titulo="Notas",seccion_json="nota",rutaDatos=rutaComentarios,servicio=Servicio)
        json_actualizado = SeccionNotas.render()

        SeccionImportante=Comentarios(titulo="Importante",seccion_json="importante",rutaDatos=rutaComentarios,servicio=Servicio)
        json_actualizado = SeccionImportante.render()

        SeccionPrecaucion=Comentarios(titulo="Precaución",seccion_json="precaucion",rutaDatos=rutaComentarios,servicio=Servicio)
        json_actualizado = SeccionPrecaucion.render()
        
        # Obtener el JSON completo actualizado del session_state
        if json_key in st.session_state:
            json_completo_final = st.session_state[json_key]
        else:
            json_completo_final = json_actualizado
        
        st.divider()
        
        # Inicializar estado del modal
        if 'mostrar_modal_pdf' not in st.session_state:
            st.session_state.mostrar_modal_pdf = False
        if 'pdf_enviado' not in st.session_state:
            st.session_state.pdf_enviado = False
        if 'email_pdf_enviado' not in st.session_state:
            st.session_state.email_pdf_enviado = ""
        
        # Mostrar mensaje de éxito si ya se envió
        if st.session_state.pdf_enviado:
            st.success(f"✅ **Solicitud enviada**\n\n"
                      f"PDF será enviado a:\n"
                      f"**{st.session_state.email_pdf_enviado}**\n\n"
                      f"📬 Recibirá el correo en los próximos minutos.")
            if st.button("Cerrar", key="cerrar_mensaje_pdf"):
                st.session_state.pdf_enviado = False
                st.session_state.email_pdf_enviado = ""
                st.rerun()
        
        # Botón para abrir modal
        if not st.session_state.pdf_enviado:
            if st.button("Generar PDF con comentarios actualizados", use_container_width=True):
                st.session_state.mostrar_modal_pdf = True
                st.rerun()
        
        # Modal para solicitar email
        if st.session_state.mostrar_modal_pdf and not st.session_state.pdf_enviado:
            st.info("📧 Ingrese el correo y la fecha del reporte para enviar el PDF.")
            
            with st.form(key="form_modal_pdf", clear_on_submit=False):
                email_pdf = st.text_input(
                    "Correo Electrónico",
                    placeholder="ejemplo@correo.com",
                    type="default"
                )
                
                fecha_reporte = st.date_input(
                    "Fecha del Reporte",
                    value=None,
                    help="Seleccione la fecha que aparecerá en el reporte PDF"
                )
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    enviar_btn = st.form_submit_button("✅ Enviar", use_container_width=True, type="primary")
                with col_btn2:
                    cancelar_btn = st.form_submit_button("❌ Cancelar", use_container_width=True)
                
                if cancelar_btn:
                    st.session_state.mostrar_modal_pdf = False
                    st.rerun()
                
                if enviar_btn:
                    # Validar email
                    if not email_pdf or email_pdf.strip() == "":
                        st.error("Por favor, ingrese un correo electrónico válido.")
                    elif "@" not in email_pdf:
                        st.error("Por favor, ingrese un correo electrónico válido.")
                    elif fecha_reporte is None:
                        st.error("Por favor, seleccione la fecha del reporte.")
                    else:
                        try:
                            # Validar que hay al menos 1 item en cada sección
                            if json_key not in st.session_state:
                                st.error("No se encontraron comentarios para guardar. Por favor, recargue la página.")
                            else:
                                json_para_guardar = st.session_state[json_key]
                                
                                # Validar que solo la sección "nota" tenga al menos 1 item
                                # "importante" y "precaución" son opcionales según los prompts del LLM
                                errores_validacion = []
                                
                                # Solo validar "nota" como requerida
                                contenido_nota = json_para_guardar.get("nota", [])
                                if not isinstance(contenido_nota, list) or len(contenido_nota) == 0:
                                    errores_validacion.append(f"La sección 'nota' debe tener al menos un item.")
                                
                                if errores_validacion:
                                    st.error("❌ " + " ".join(errores_validacion))
                                else:
                                    # Verificar que las variables estén disponibles
                                    if not rutaComentarios:
                                        st.error("No se pudo obtener la ruta de comentarios.")
                                    elif not json_para_guardar:
                                        st.error("No hay datos de comentarios para guardar.")
                                    else:
                                        # Guardar comentarios actualizados en S3
                                        Servicio.GuardarDatos(
                                            json_para_guardar,
                                            rutaComentarios
                                        )
                                        
                                        # Construir mensaje para SQS PDF
                                        # Convertir fecha a formato YYYY-MM-DD
                                        fecha_formato = fecha_reporte.strftime("%Y-%m-%d")
                                        
                                        mensaje_pdf_sqs = {
                                            "report_id": report_id,
                                            "bucket": Servicio.bucket,
                                            "region": Servicio.Region,
                                            "report_type": "energia",
                                            "email": email_pdf.strip(),
                                            "report_date": fecha_formato
                                        }
                                        
                                        # Obtener URL de la cola PDF desde secrets
                                        queue_url_pdf = st.secrets["aws"]["sqs_pdf_queue_url"]
                                        
                                        # Enviar mensaje a SQS
                                        Servicio.enviar_mensaje_sqs(queue_url_pdf, mensaje_pdf_sqs)
                                        
                                        # Cerrar modal y marcar como enviado
                                        st.session_state.mostrar_modal_pdf = False
                                        st.session_state.pdf_enviado = True
                                        st.session_state.email_pdf_enviado = email_pdf.strip()
                                        st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error al enviar la solicitud: {str(e)}\n\nPor favor, intente nuevamente.")

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
            
        