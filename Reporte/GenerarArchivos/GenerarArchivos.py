import streamlit as st
from Servicio import Data


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



def modal_generacion_pdf_unificado(report_id, servicio, datos_rutas):
    """
    Muestra el botón y el modal para enviar TODOS los reportes juntos.
    
    Args:
        report_id (str): El ID único del reporte general.
        servicio (Servicio): Instancia de tu clase de conexión a AWS.
        datos_rutas (dict): El diccionario con las rutas originales a S3. 
                            Ej: Datos["Comentarios"]
    """
    
    # 1. Inicializar estado del modal
    if 'mostrar_modal_pdf' not in st.session_state:
        st.session_state.mostrar_modal_pdf = False
    if 'pdf_enviado' not in st.session_state:
        st.session_state.pdf_enviado = False
    if 'email_pdf_enviado' not in st.session_state:
        st.session_state.email_pdf_enviado = ""

    # 2. Mostrar mensaje de éxito si ya se envió
    if st.session_state.pdf_enviado:
        st.success(f"✅ **Solicitud enviada**\n\n"
                   f"Los PDFs serán enviados a:\n"
                   f"**{st.session_state.email_pdf_enviado}**\n\n"
                   f"📬 Recibirá el correo en los próximos minutos.")
        if st.button("Cerrar", key="cerrar_mensaje_pdf_global"):
            st.session_state.pdf_enviado = False
            st.session_state.email_pdf_enviado = ""
            st.rerun()
        return # Detenemos la ejecución aquí si ya se envió

    # 3. Botón para abrir modal
    if not st.session_state.pdf_enviado:
        if st.button("Generar .ZIP de todos los reportes", use_container_width=True, type="primary"):
            st.session_state.mostrar_modal_pdf = True
            st.rerun()

    # 4. Modal para solicitar email, fecha y CFE
    if st.session_state.mostrar_modal_pdf and not st.session_state.pdf_enviado:
        st.info("📧 Ingrese los datos para enviar los reportes unificados.")
        
        with st.form(key="form_modal_pdf_unificado", clear_on_submit=False):
            email_pdf = st.text_input(
                "Correo Electrónico",
                placeholder="ejemplo@correo.com",
            )
            
            fecha_reporte = st.date_input(
                "Fecha del Reporte",
                value=None,
                help="Seleccione la fecha que aparecerá en los reportes PDF"
            )
            
            # Nuevo campo basado en el payload del ingeniero
            enable_cfe = st.checkbox(
                "Habilitar gráficas CFE (enable_cfe_charts)", 
                value=True
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                enviar_btn = st.form_submit_button("✅ Enviar Todo", use_container_width=True, type="primary")
            with col_btn2:
                cancelar_btn = st.form_submit_button("❌ Cancelar", use_container_width=True)

            if cancelar_btn:
                st.session_state.mostrar_modal_pdf = False
                st.rerun()

            if enviar_btn:
                # Validaciones básicas
                if not email_pdf or "@" not in email_pdf:
                    st.error("Por favor, ingrese un correo electrónico válido.")
                elif fecha_reporte is None:
                    st.error("Por favor, seleccione la fecha del reporte.")
                else:
                    try:
                        # --- PASO A: RECOLECTAR Y GUARDAR EN S3 ---
                        rutas = {
                            "codigo_red": datos_rutas["CodigoRed"],
                            "energia": datos_rutas["Energia"],
                            "pq": datos_rutas["PQ"]
                        }
                        
                        archivos_guardados = 0
                        
                        # Iterar sobre las 3 rutas para guardar los cambios en S3
                        for tipo, ruta_s3 in rutas.items():
                            json_key = f"comentarios_json_{ruta_s3}"
                            
                            # Solo guardamos si el usuario visitó la pantalla y se cargó el JSON en memoria
                            if json_key in st.session_state:
                                json_para_guardar = st.session_state[json_key]
                                
                                # Validación de la sección 'nota' (requerida por tu lógica anterior)
                                contenido_nota = json_para_guardar.get("nota", [])
                                if not isinstance(contenido_nota, list) or len(contenido_nota) == 0:
                                    st.error(f"❌ La sección 'nota' en {tipo} debe tener al menos un item.")
                                    st.stop() # Detiene la ejecución si hay error
                                
                                # Guardar en S3 usando tu servicio
                                servicio.GuardarDatos(json_para_guardar, ruta_s3)
                                archivos_guardados += 1
                        
                        if archivos_guardados == 0:
                            st.warning("No se encontraron comentarios cargados en memoria para guardar. Asegúrate de visitar las pestañas de los reportes primero.")
                            st.stop()

                        # --- PASO B: CONSTRUIR Y ENVIAR PAYLOAD A SQS ---
                        fecha_formato = fecha_reporte.strftime("%Y-%m-%d")
                        
                        # Payload unificado según las instrucciones del ingeniero de nube
                        mensaje_pdf_sqs = {
                            "report_id": report_id,
                            "bucket": servicio.bucket,
                            "region": servicio.Region,
                            "report_types": ["codigo_red", "pq", "energia"],
                            "email": email_pdf.strip(),
                            "report_date": fecha_formato,
                            "enable_cfe_charts": enable_cfe
                        }
                        
                        # Obtener URL de la cola y enviar
                        queue_url_pdf = st.secrets["aws"]["sqs_pdf_queue_url"]
                        servicio.enviar_mensaje_sqs(queue_url_pdf, mensaje_pdf_sqs)
                        
                        # Cerrar modal y marcar como enviado
                        st.session_state.mostrar_modal_pdf = False
                        st.session_state.pdf_enviado = True
                        st.session_state.email_pdf_enviado = email_pdf.strip()
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error al procesar la solicitud: {str(e)}")


def GenerarArchivos(report_id):

       Servicio=get_servicio_aws(report_id, _version=1)
       Datos=get_diccionario_rutas(_Servicio=Servicio,nombre_carpeta=report_id)

       # --- AQUÍ VA NUESTRA NUEVA LÓGICA UNIFICADA ---
       st.header("📁 Gestión de Archivos y Reportes")
       st.info("Genera el PDF unificado. Asegúrate de haber guardado tus comentarios en las otras pestañas.")

       # Asumiendo que ya tienes definidas tus variables report_id, Servicio y Datos
       modal_generacion_pdf_unificado(
       report_id=report_id,
       servicio=Servicio,
       datos_rutas=Datos["Comentarios"]
       )