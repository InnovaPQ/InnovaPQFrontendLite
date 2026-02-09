import streamlit as st
import uuid
import pandas as pd
import io
import json
import re
from Servicio import Data

# Mapeo de perfiles: nombre bonito -> key técnica
PERFILES_MEDIDOR = {
    "Schneider ION-9000": "schneider_ion9000",
    "ACUVIM-EL": "acuvim_el",
    "ACUVIM-2W": "acuvim_2w",
    "SEL-735": "sel_735",
    "Circutor": "circutor"
} 

# --- 1. INSTANCIA DE SERVICIO (Recurso Compartido) ---
@st.cache_resource
def get_servicio_base():
    # Instanciamos sin carpeta específica
    return Data(folder="reports/")

# --- 2. HELPER FUNCTIONS (Message Builder - Single Responsibility) ---
def build_sqs_message(
    report_id: str,
    bucket: str,
    region: str,
    input_key: str,
    email: str,
    report_base_url: str,
    nominal_voltage: float,
    nominal_voltage_unit: str,
    profile: str,
    skip_llm: bool = True
) -> dict:
    """
    Construye el mensaje SQS para el procesamiento de reportes.
    
    Args:
        report_id: ID único del reporte
        bucket: Nombre del bucket S3
        region: Región de AWS
        input_key: Ruta del archivo de entrada en S3
        email: Email para notificaciones
        report_base_url: URL base para los reportes
        nominal_voltage: Tensión nominal del sistema
        nominal_voltage_unit: Unidad de la tensión nominal (kV o V)
        profile: Perfil técnico del medidor
        skip_llm: Si es True, omite la generación de reportes LLM (default: True - skip LLM by default)
    
    Returns:
        dict: Mensaje SQS formateado
    """
    return {
        "report_id": report_id,
        "bucket": bucket,
        "region": region,
        "input_key": input_key,
        "img_format": "png",
        "dpi": 200,
        "output_mode": "s3",
        "email": email,
        "report_base_url": report_base_url,
        "nominal_voltage": nominal_voltage,
        "nominal_voltage_unit": nominal_voltage_unit,
        "profile": profile,
        "skip_llm": skip_llm
    }

def CargarDatos2():
    # Inicializamos el servicio
    Servicio = get_servicio_base()
    
    st.title("⚡ Nuevo Reporte de Calidad de Energía")
    st.info("Todos los campos marcados son obligatorios. Se generará la estructura requerida en S3.")

    # ==========================================
    # 1. FORMULARIO (UI)
    # ==========================================
    with st.form(key="formulario_carga", clear_on_submit=False):
        
        datos_formulario = {}
        archivos_formulario = {}

        tab1, tab2, tab3 = st.tabs(["📋 Información General", "⚙️ Datos Técnicos", "📂 Archivos"])

        # ---------------------------------------------------------
        # TAB 1: DATOS ADMINISTRATIVOS (Tablas 1 y 2)
        # ---------------------------------------------------------
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                # No guardamos correo en Excel según tus tablas, pero sirve para notificación
                datos_formulario["Correo Electrónico"] = st.text_input("Correo Electrónico")
                datos_formulario["Empresa"] = st.text_input("Empresa / Cliente")
            
            with col2:
                datos_formulario["Responsable de equipo"] = st.text_input("Responsable del sitio")
                datos_formulario["Dirección"] = st.text_input("Dirección del sitio")
            
            st.divider()
            datos_formulario["Descripción de actividades"] = st.text_area("Descripción de actividades", height=80)
            datos_formulario["Nombre del punto"] = st.text_input("Nombre del punto de medición")
            datos_formulario["Descripción carga"] = st.text_input("Descripción general de la carga")

        # ---------------------------------------------------------
        # TAB 2: DATOS TÉCNICOS (Tablas 3 y 4)
        # ---------------------------------------------------------
        with tab2:
            st.subheader("Medidor")
            c1, c2, c3 = st.columns(3)
            # Perfil del medidor (reemplaza "Marca")
            perfil_seleccionado = c1.selectbox("Perfil del Medidor", list(PERFILES_MEDIDOR.keys()))
            datos_formulario["Marca"] = perfil_seleccionado  # Guardamos el nombre bonito para las tablas
            datos_formulario["_perfil_tecnico"] = PERFILES_MEDIDOR[perfil_seleccionado]  # Guardamos el valor técnico para SQS
            datos_formulario["Clase"] = c2.selectbox("Clase", ["A", "S"])
            datos_formulario["Tasa muestreo"] = c3.selectbox("Tasa", ["1 min", "5 min", "10 min", "15 min"])

            st.divider()
            st.subheader("Parámetros Eléctricos")
            
            col_a, col_b = st.columns(2)
            with col_a:
                datos_formulario["Frecuencia del sistema"] = st.radio("Frecuencia", ["60 Hz", "50 Hz"], horizontal=True)
                
                # Tensión Suministro
                cc1, cc2 = st.columns([0.7, 0.3])
                t_sum = cc1.text_input("Tensión Suministro (Valor)")
                u_sum = cc2.selectbox("U.", ["V", "kV"], key="usum")
                datos_formulario["Tensión de suministro"] = f"{t_sum} {u_sum}" if t_sum else ""

                # Demanda
                cc1, cc2 = st.columns([0.7, 0.3])
                dem = cc1.text_input("Demanda Contratada (Valor)")
                u_dem = cc2.selectbox("U.", ["kW", "MW", "W"], key="udem")
                datos_formulario["Demanda contratada"] = f"{dem} {u_dem}" if dem else ""

                # Corriente Demanda
                cc1, cc2 = st.columns([0.7, 0.3])
                i_dem = cc1.text_input("Corriente demanda máx (Valor)")
                u_idem = cc2.selectbox("U.", ["A", "kA"], key="uidem")
                datos_formulario["Corriente demanda máxima contratada"] = f"{i_dem} {u_idem}" if i_dem else ""

            with col_b:
                datos_formulario["Transformador del tablero"] = st.text_input("Transformador (Capacidad/Tipo)")
                
                # Tensión Punto
                cc1, cc2 = st.columns([0.7, 0.3])
                t_pto = cc1.text_input("Tensión Punto (Valor)")
                u_pto = cc2.selectbox("U.", ["V", "kV"], key="upto")
                datos_formulario["Tensión de punto de medición"] = f"{t_pto} {u_pto}" if t_pto else ""

                # Corriente CC
                cc1, cc2 = st.columns([0.7, 0.3])
                icc = cc1.text_input("Corriente CC (Valor)")
                u_icc = cc2.selectbox("U.", ["kA", "A"], key="uicc")
                datos_formulario["Corriente de corto circuito"] = f"{icc} {u_icc}" if icc else ""

            st.divider()
            cd1, cd2 = st.columns(2)
            datos_formulario["Temporalidad de medición"] = st.selectbox("Temporalidad", ["Diaria", "Semanal", "Mensual"])
            # Convertimos a str para que sea serializable
            datos_formulario["Fecha de medición inicial"] = str(cd1.date_input("Inicio Medición"))
            datos_formulario["Fecha de medición final"] = str(cd2.date_input("Fin Medición"))

        # ---------------------------------------------------------
        # TAB 3: ARCHIVOS (Validación Crítica)
        # ---------------------------------------------------------
        with tab3:
            st.warning("⚠️ Todos los archivos son obligatorios.")
            
            st.subheader("Carpeta: raw_data")
            archivos_formulario["main_file"] = st.file_uploader("Archivo Principal (CSV/PQDIF/XLSX)", type=["csv", "pqd", "pqdif", "xlsx"])
            
            st.divider()
            st.subheader("Carpeta: input")
            col_files_1, col_files_2 = st.columns(2)
            with col_files_1:
                archivos_formulario["Diagrama Unifilar"] = st.file_uploader("Diagrama Unifilar", type=["png", "jpg", "pdf"])
            with col_files_2:
                archivos_formulario["Sello"] = st.file_uploader("Sello (Stamp)", type=["png", "jpg"])

        st.divider()
        submit_button = st.form_submit_button("🚀 Iniciar Procesamiento", use_container_width=True, type="primary")

    # ==========================================
    # 2. LÓGICA DE PROCESAMIENTO Y CARGA
    # ==========================================
    
    # Inicializar estados del modal
    if 'mostrar_modal_email' not in st.session_state:
        st.session_state.mostrar_modal_email = False
    if 'email_confirmado' not in st.session_state:
        st.session_state.email_confirmado = None
    if 'procesar_carga' not in st.session_state:
        st.session_state.procesar_carga = False
    if 'skip_llm' not in st.session_state:
        st.session_state.skip_llm = True  # Default: LLM IS skipped (only generate tables/graphs)
    
    # Modal para confirmar/cambiar email (se muestra después de validación)
    if st.session_state.mostrar_modal_email and not st.session_state.procesar_carga:
        st.info("📧 Por favor, confirme o ingrese el correo electrónico al cual desea enviar el reporte.")
        
        with st.form(key="form_modal_email_carga", clear_on_submit=False):
            # Campo de correo vacío (no se prellena automáticamente)
            email_envio = st.text_input(
                "Correo Electrónico para envío del reporte",
                value="",
                placeholder="ejemplo@correo.com",
                type="default"
            )
            
            st.divider()
            
            # Toggle para skip LLM
            skip_llm_toggle = st.toggle(
                "⏭️ Omitir generación de reportes LLM",
                value=st.session_state.skip_llm,
                help="Si está activado, se generarán solo las tablas y gráficos sin los reportes de análisis LLM. Por defecto está activado (se omite LLM)."
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                confirmar_btn = st.form_submit_button("✅ Confirmar y Procesar", use_container_width=True, type="primary")
            with col_btn2:
                cancelar_btn = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if cancelar_btn:
                st.session_state.mostrar_modal_email = False
                st.session_state.email_confirmado = None
                st.session_state.procesar_carga = False
                st.session_state.skip_llm = True  # Resetear a default (skip LLM)
                st.rerun()
            
            if confirmar_btn:
                # Validar email
                if not email_envio or email_envio.strip() == "":
                    st.error("Por favor, ingrese un correo electrónico válido.")
                elif "@" not in email_envio:
                    st.error("Por favor, ingrese un correo electrónico válido.")
                else:
                    st.session_state.email_confirmado = email_envio.strip()
                    st.session_state.skip_llm = skip_llm_toggle  # Guardar preferencia del usuario
                    st.session_state.mostrar_modal_email = False
                    st.session_state.procesar_carga = True
                    st.rerun()
    
    if submit_button:
        
        # A. VALIDACIÓN ESTRICTA
        errores = []
        for campo, valor in datos_formulario.items():
            # Ignorar campos internos que empiezan con _
            if campo.startswith("_"):
                continue
            if not valor or str(valor).strip() == "": errores.append(campo)
        
        for nombre_archivo, objeto_archivo in archivos_formulario.items():
            if objeto_archivo is None: errores.append(nombre_archivo)

        if errores:
            st.error(f"❌ Faltan los siguientes campos obligatorios: {', '.join(errores)}")
            return 
        
        # Si pasa validación, mostrar modal para confirmar email
        st.session_state.mostrar_modal_email = True
        st.rerun()
    
    # Procesar carga solo si el email está confirmado y se debe procesar
    if st.session_state.procesar_carga and st.session_state.email_confirmado:
        email_final = st.session_state.email_confirmado
        
        # Limpiar estados
        st.session_state.email_confirmado = None
        st.session_state.procesar_carga = False
        st.session_state.mostrar_modal_email = False
        
        # B. PREPARACIÓN DE CARPETAS S3
        report_uuid = str(uuid.uuid4())
        prefix_root = f"report{report_uuid}/"
        prefix_raw = f"{prefix_root}raw_data/"
        prefix_input = f"{prefix_root}input/"

        client = Servicio.client_s3
        bucket = Servicio.bucket

        with st.status(f"Generando reporte ID: {report_uuid}...", expanded=True) as status:
            try:
                # ---------------------------------------------------------
                # PASO 1: Subir Archivo Principal a "raw_data"
                # ---------------------------------------------------------
                file_main = archivos_formulario["main_file"]
                file_main.seek(0)
                status.write(f"⬆️ Subiendo Raw Data: {file_main.name}")
                client.upload_fileobj(file_main, bucket, f"{prefix_raw}{file_main.name}")

                # ---------------------------------------------------------
                # PASO 2: Subir Archivos Físicos a "input"
                # ---------------------------------------------------------
                # Diagrama - siempre se guarda como diagrama_unifilar.png
                file_diag = archivos_formulario["Diagrama Unifilar"]
                file_diag.seek(0)
                client.upload_fileobj(file_diag, bucket, f"{prefix_input}diagrama_unifilar.png")
                
                # Sello - siempre se guarda como stamp.png
                file_stamp = archivos_formulario["Sello"]
                file_stamp.seek(0)
                client.upload_fileobj(file_stamp, bucket, f"{prefix_input}stamp.png")

                # ---------------------------------------------------------
                # PASO 3: GENERACIÓN DE EXCELS (Tablas 1, 2, 3, 4)
                # ---------------------------------------------------------
                status.write("⚙️ Generando Tablas de Información...")

                # Función interna para crear Excel en RAM y subir
                def subir_excel(nombre_s3, data_dict):
                    df = pd.DataFrame(list(data_dict.items()), columns=["Concepto", "Valor"])
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    output.seek(0)
                    client.upload_fileobj(output, bucket, f"{prefix_input}{nombre_s3}")

                # Generar Tabla 1
                subir_excel("Tabla 1 - Información Centro Carga.xlsx", {
                    "Empresa": datos_formulario["Empresa"],
                    "Dirección": datos_formulario["Dirección"],
                    "Responsable de equipo": datos_formulario["Responsable de equipo"]
                })

                # Generar Tabla 2
                subir_excel("Tabla 2 - Descripción Centro Carga.xlsx", {
                    "Descripción de actividades": datos_formulario["Descripción de actividades"],
                    "Nombre del punto de medición": datos_formulario["Nombre del punto"],
                    "Descripción general de la carga": datos_formulario["Descripción carga"]
                })

                # Generar Tabla 3
                subir_excel("Tabla 3 - Información Medidor.xlsx", {
                    "Marca": datos_formulario["Marca"],
                    "Clase": datos_formulario["Clase"],
                    "Tasa de muestreo": datos_formulario["Tasa muestreo"]
                })

                # Generar Tabla 4
                subir_excel("Tabla 4 - Datos Medición.xlsx", {
                    "Frecuencia del sistema": datos_formulario["Frecuencia del sistema"],
                    "Tensión de suministro": datos_formulario["Tensión de suministro"],
                    "Tensión de punto de medición": datos_formulario["Tensión de punto de medición"],
                    "Demanda contratada": datos_formulario["Demanda contratada"],
                    "Corriente demanda máxima contratada": datos_formulario["Corriente demanda máxima contratada"],
                    "Corriente de corto circuito": datos_formulario["Corriente de corto circuito"],
                    "Transformador del tablero": datos_formulario["Transformador del tablero"],
                    "Temporalidad de medición": datos_formulario["Temporalidad de medición"],
                    "Fecha de medición inicial": datos_formulario["Fecha de medición inicial"],
                    "Fecha de medición final": datos_formulario["Fecha de medición final"]
                })

                # ---------------------------------------------------------
                # PASO 4: ENVIAR MENSAJE A SQS PARA PROCESAMIENTO
                # ---------------------------------------------------------
                status.write("📨 Enviando mensaje a la cola de procesamiento...")
                
                # Función para extraer tensión nominal (número y unidad)
                def extraer_tension_nominal(tension_str):
                    """
                    Extrae el número y la unidad de una cadena como "34.75 kV" o "34,75 kV"
                    Retorna: (valor_numerico, unidad) o (None, None) si no se puede parsear
                    """
                    if not tension_str or tension_str.strip() == "":
                        return None, None
                    
                    # Reemplazar comas por puntos
                    tension_limpia = tension_str.replace(",", ".")
                    
                    # Buscar patrón: número (puede tener decimales) seguido de unidad
                    match = re.match(r'([\d.]+)\s*([a-zA-Z]+)', tension_limpia.strip())
                    if match:
                        try:
                            valor = float(match.group(1))
                            unidad = match.group(2)
                            return valor, unidad
                        except ValueError:
                            return None, None
                    return None, None
                
                # Extraer tensión nominal de "Tensión de punto de medición"
                tension_valor, tension_unidad = extraer_tension_nominal(datos_formulario["Tensión de punto de medición"])
                
                if tension_valor is None:
                    raise ValueError("No se pudo extraer la tensión nominal del punto de medición. Verifique el formato.")
                
                # Construir mensaje para SQS usando el helper function
                # input_key debe incluir la ruta raw_data/ ya que el report_id tiene el prefijo report{uuid}
                input_key_path = f"{file_main.name}"
                
                # Mapear report_base_url según el modo (dev/prod)
                mode = st.secrets["aws"].get("mode", "dev")
                if mode == "dev":
                    report_base_url = "http://localhost:8501"
                else:  # prod
                    # Por ahora usar el mismo, pero se puede configurar en secrets
                    report_base_url = st.secrets["aws"].get("report_base_url", "http://localhost:8501")
                
                # Obtener skip_llm del session state (default: True - skip LLM by default)
                skip_llm_value = st.session_state.get("skip_llm", True)
                
                # Construir mensaje usando la función helper (Single Responsibility)
                mensaje_sqs = build_sqs_message(
                    report_id=f"report{report_uuid}",
                    bucket=bucket,
                    region=Servicio.Region,
                    input_key=input_key_path,
                    email=email_final,  # Usar el email confirmado del modal
                    report_base_url=report_base_url,
                    nominal_voltage=tension_valor,
                    nominal_voltage_unit=tension_unidad,
                    profile=datos_formulario["_perfil_tecnico"],
                    skip_llm=skip_llm_value
                )
                
                # Obtener URL de la cola desde secrets
                queue_url = st.secrets["aws"]["sqs_queue_url"]
                
                # Enviar mensaje a SQS (las operaciones upload_fileobj son síncronas, 
                # así que los archivos ya están en S3 en este punto)
                Servicio.enviar_mensaje_sqs(queue_url, mensaje_sqs)
                
                status.update(label="¡Carga Completa!", state="complete", expanded=False)
                
                st.balloons()
                st.success(f"Archivos recibidos. ID del reporte: {report_uuid}")
                st.info(f"El link para ver el reporte se le enviará a {email_final}")

            except Exception as e:
                status.update(label="Error crítico", state="error")
                st.error(f"Hubo un error al conectar con AWS: {str(e)}")