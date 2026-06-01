import streamlit as st
import uuid
import pandas as pd
import io
import json
import re
from enum import Enum
from Servicio import Data


class CorrienteUnidad(str, Enum):
    """Unidades de Icc / I_L para SQS (backend: icc_unit / il_unit → 'A' o 'kA')."""

    A = "A"
    KA = "kA"


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
    input_filenames: list,
    email: str,
    report_base_url: str,
    nominal_voltage: float,
    nominal_voltage_unit: str,
    profile: str,
    cfe_file: str,
    enable_cfe_charts: bool,
    demand: float,
    demand_unit: str,
    supply_voltage:float,
    supply_voltage_unit:str,
    icc: float,
    il: float,
    icc_unit: str,
    il_unit: str,
    skip_llm: bool = True,
) -> dict:
    """
    Construye el mensaje SQS para el procesamiento de reportes.
    
    Args:
        report_id: ID único del reporte
        bucket: Nombre del bucket S3
        region: Región de AWS
        input_filenames: Nombres en raw_data/ (1 → input_key; ≥2 → input_keys en SQS)
        email: Email para notificaciones
        report_base_url: URL base para los reportes
        nominal_voltage: Tensión nominal del sistema
        nominal_voltage_unit: Unidad de la tensión nominal (kV o V)
        profile: Perfil técnico del medidor
        demand: Demanda contratada en la unidad seleccionada
        demand_unit: Unidad de demanda contratada (W, kW o MW)
        skip_llm: Si es True, omite la generación de reportes LLM (default: True - skip LLM by default)
    
    Returns:
        dict: Mensaje SQS formateado
    """
    if not input_filenames:
        raise ValueError("Se requiere al menos un archivo de medición.")

    mensaje = {
        "report_id": report_id,
        "bucket": bucket,
        "region": region,
        "img_format": "png",
        "dpi": 200,
        "output_mode": "s3",
        "email": email,
        "report_types": ["codigo_red", "pq", "energia"],
        "report_base_url": report_base_url,
        "nominal_voltage": nominal_voltage,
        "nominal_voltage_unit": nominal_voltage_unit,
        "profile": profile,
        "skip_llm": skip_llm,
        "enable_cfe_charts": enable_cfe_charts,
        "cfe_file": cfe_file,
        "demand": demand,
        "demand_unit": demand_unit,
        "supply_voltage":supply_voltage,
        "supply_voltage_unit":supply_voltage_unit,
        "icc": icc,
        "il": il,
        "icc_unit": icc_unit,
        "il_unit": il_unit,
    }
    if len(input_filenames) >= 2:
        mensaje["input_keys"] = list(input_filenames)
    else:
        mensaje["input_key"] = input_filenames[0]
    return mensaje

CFE_FILE_NAME = "raw_cfe_data.csv"

_CARGA_SESSION_DEFAULTS = {
    "carga_fase": None,
    "report_uuid": None,
    "report_id": None,
    "prefix_root": None,
    "prefix_raw": None,
    "prefix_input": None,
    "input_key_path": None,
    "input_keys_paths": None,
    "cfe_agregado": False,
    "column_check_result": None,
    "carga_snapshot": None,
    "email_final": None,
    "mostrar_modal_email": False,
    "email_confirmado": None,
    "procesar_carga": False,
    "skip_llm": True,
    "email_confirm_error": None,
    "column_check_payload": None,
}


def _init_carga_session():
    for key, default in _CARGA_SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default


def _clear_carga_session():
    for key, default in _CARGA_SESSION_DEFAULTS.items():
        st.session_state[key] = default


def _serialize_datos_valor(valor):
    if isinstance(valor, CorrienteUnidad):
        return valor.value
    return valor


def _deserialize_datos(datos_ser: dict) -> dict:
    out = dict(datos_ser)
    for key in (
        "Corriente demanda máxima contratada unidad",
        "Corriente de corto circuito unidad",
    ):
        if key in out and isinstance(out[key], str):
            out[key] = CorrienteUnidad(out[key])
    return out


def _serialize_uploaded_file(archivo) -> dict:
    archivo.seek(0)
    return {"name": archivo.name, "bytes": archivo.getvalue()}


def _serialize_form_snapshot(datos_formulario: dict, archivos_formulario: dict) -> dict:
    datos_ser = {k: _serialize_datos_valor(v) for k, v in datos_formulario.items()}
    archivos_ser = {}
    for nombre, archivo in archivos_formulario.items():
        if archivo is None:
            archivos_ser[nombre] = None
        elif nombre == "main_files":
            archivos_ser[nombre] = [
                _serialize_uploaded_file(f) for f in archivo
            ]
        else:
            archivos_ser[nombre] = _serialize_uploaded_file(archivo)
    return {"datos": datos_ser, "archivos": archivos_ser}


def _main_files_from_snapshot(archivos: dict) -> list:
    """Lista de file-like desde snapshot (main_files o legacy main_file)."""
    entry = archivos.get("main_files")
    if entry is None and archivos.get("main_file") is not None:
        entry = archivos.get("main_file")
    if not entry:
        return []
    if isinstance(entry, list):
        return [_archivo_from_snapshot(e) for e in entry if e]
    f = _archivo_from_snapshot(entry)
    return [f] if f else []


def _build_input_payload_fields(filenames: list) -> dict:
    if not filenames:
        raise ValueError("Se requiere al menos un archivo de medición.")
    if len(filenames) >= 2:
        return {"input_keys": list(filenames)}
    return {"input_key": filenames[0]}


def _archivo_from_snapshot(entry):
    if not entry:
        return None
    if isinstance(entry, list):
        return None
    buf = io.BytesIO(entry["bytes"])
    buf.name = entry["name"]
    return buf


def _archivos_from_snapshot(archivos_ser: dict) -> dict:
    """Reconstruye archivos del snapshot (main_files queda como lista serializada)."""
    out = {}
    for nombre, entry in archivos_ser.items():
        if nombre in ("main_files", "main_file"):
            out[nombre] = entry
        else:
            out[nombre] = _archivo_from_snapshot(entry)
    return out


def _extraer_tension_nominal(tension_str):
    if not tension_str or str(tension_str).strip() == "":
        return None, None
    tension_limpia = str(tension_str).replace(",", ".")
    match = re.match(r"([\d.]+)\s*([a-zA-Z]+)", tension_limpia.strip())
    if match:
        try:
            return float(match.group(1)), match.group(2)
        except ValueError:
            return None, None
    return None, None


def _ensure_report_paths():
    if not st.session_state.report_uuid:
        uid = str(uuid.uuid4())
        st.session_state.report_uuid = uid
        st.session_state.report_id = f"report{uid}"
        st.session_state.prefix_root = f"report{uid}/"
        st.session_state.prefix_raw = f"report{uid}/raw_data/"
        st.session_state.prefix_input = f"report{uid}/input/"


def _build_column_check_payload(datos: dict, input_names: list, report_id: str, bucket: str, region: str) -> dict:
    payload = {
        "action": "check_columns",
        "report_id": report_id,
        "bucket": bucket,
        "region": region,
        "profile": datos["_perfil_tecnico"],
        "output_mode": "s3",
        **_build_input_payload_fields(input_names),
    }
    il_val = datos.get("Corriente demanda máxima contratada valor")
    if il_val is not None and float(il_val) > 0:
        payload["il"] = float(il_val)
    return payload


def _run_upload_raw_only(Servicio: Data):
    """Sube raw_data y pasa a fase checking_columns (rerun para no bloquear la UI)."""
    snap = st.session_state.carga_snapshot
    if not snap:
        st.error("No hay datos de carga en sesión. Vuelva a enviar el formulario.")
        st.session_state.procesar_carga = False
        st.session_state.carga_fase = None
        return

    datos = _deserialize_datos(snap["datos"])
    archivos = _archivos_from_snapshot(snap["archivos"])
    _ensure_report_paths()

    prefix_raw = st.session_state.prefix_raw
    client = Servicio.client_s3
    bucket = Servicio.bucket

    with st.status(f"Subiendo archivos — {st.session_state.report_uuid}...", expanded=True) as status:
        try:
            main_files = _main_files_from_snapshot(archivos)
            file_cfe = archivos.get("CFE")
            if not main_files:
                raise ValueError("Falta al menos un archivo de medición en el snapshot.")

            input_names = []
            for f in main_files:
                f.seek(0)
                status.write(f"Subiendo raw_data: {f.name}")
                client.upload_fileobj(f, bucket, f"{prefix_raw}{f.name}")
                input_names.append(f.name)
            st.session_state.input_keys_paths = input_names
            st.session_state.input_key_path = input_names[0]

            if file_cfe is not None:
                file_cfe.seek(0)
                status.write(f"Subiendo CFE: {CFE_FILE_NAME}")
                client.upload_fileobj(file_cfe, bucket, f"{prefix_raw}{CFE_FILE_NAME}")
                st.session_state.cfe_agregado = True
            else:
                st.session_state.cfe_agregado = False

            st.session_state.column_check_payload = _build_column_check_payload(
                datos, input_names, st.session_state.report_id, bucket, Servicio.Region
            )
            st.session_state.procesar_carga = False
            st.session_state.carga_fase = "checking_columns"
            status.update(label="Archivos en S3", state="complete", expanded=False)
            st.rerun()
        except Exception as e:
            status.update(label="Error al subir", state="error")
            st.error(f"Error: {e}")
            st.session_state.procesar_carga = False
            st.session_state.carga_fase = None


def _run_column_check_only(Servicio: Data):
    """Ejecuta el chequeo preventivo de columnas."""
    payload = st.session_state.get("column_check_payload")
    if not payload:
        st.error("No hay payload de chequeo. Vuelva a enviar el formulario.")
        st.session_state.carga_fase = None
        return

    st.info(
        "Analizando las columnas del archivo (puede tardar **1–3 minutos**). "
        "No recargue la página."
    )
    with st.spinner("Ejecutando chequeo de columnas..."):
        try:
            result = Servicio.check_columns(payload)
            st.session_state.column_check_result = result
            st.session_state.column_check_payload = None
            st.session_state.carga_fase = "review"
            st.rerun()
        except Exception as e:
            st.session_state.carga_fase = None
            st.error(f"Error en chequeo de columnas: {e}")


def _run_upload_rest_and_sqs(Servicio: Data):
    snap = st.session_state.carga_snapshot
    if not snap:
        st.error("No hay datos de carga en sesión.")
        st.session_state.carga_fase = None
        return

    datos = _deserialize_datos(snap["datos"])
    archivos = _archivos_from_snapshot(snap["archivos"])
    email_final = st.session_state.email_final
    if not email_final:
        st.error("No hay correo de envío configurado.")
        st.session_state.carga_fase = None
        return

    report_id = st.session_state.report_id
    prefix_input = st.session_state.prefix_input
    input_names = st.session_state.input_keys_paths or (
        [st.session_state.input_key_path] if st.session_state.input_key_path else []
    )
    cfe_agregado = st.session_state.cfe_agregado
    client = Servicio.client_s3
    bucket = Servicio.bucket

    with st.status(f"Generando reporte {st.session_state.report_uuid}...", expanded=True) as status:
        try:
            file_diag = archivos.get("Diagrama Unifilar")
            if file_diag is not None:
                file_diag.seek(0)
                status.write("Subiendo diagrama unifilar")
                client.upload_fileobj(
                    file_diag, bucket, f"{prefix_input}diagrama_unifilar.png"
                )

            file_stamp = archivos.get("Sello")
            if file_stamp is not None:
                file_stamp.seek(0)
                status.write("Subiendo sello")
                client.upload_fileobj(file_stamp, bucket, f"{prefix_input}stamp.png")

            status.write("Generando tablas de información...")

            def subir_excel(nombre_s3, data_dict):
                df = pd.DataFrame(list(data_dict.items()), columns=["Concepto", "Valor"])
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False)
                output.seek(0)
                client.upload_fileobj(output, bucket, f"{prefix_input}{nombre_s3}")

            subir_excel(
                "Tabla 1 - Información Centro Carga.xlsx",
                {
                    "Empresa": datos["Empresa"],
                    "Dirección": datos["Dirección"],
                    "Responsable de equipo": datos["Responsable de equipo"],
                    "Email": datos["Correo Electrónico"],
                },
            )
            subir_excel(
                "Tabla 2 - Descripción Centro Carga.xlsx",
                {
                    "Nombre del punto de medición": datos["Nombre del punto"],
                    "Descripción general de la carga": datos["Descripción carga"],
                },
            )
            subir_excel(
                "Tabla 3 - Información Medidor.xlsx",
                {
                    "Marca": datos["Marca"],
                    "Clase": datos["Clase"],
                    "Tasa de muestreo": datos["Tasa muestreo"],
                },
            )
            subir_excel(
                "Tabla 4 - Datos Medición.xlsx",
                {
                    "Frecuencia": datos["Frecuencia del sistema"],
                    "Tensión": datos["Tensión de suministro"],
                    "Demanda contratada": datos["Demanda contratada"],
                    "Corriente demanda máxima": datos["Corriente demanda máxima contratada"],
                    "Corriente de corto circuito máximo": datos["Corriente de corto circuito"],
                },
            )
            subir_excel(
                "Tabla 5 - Datos Punto Medición.xlsx",
                {
                    "Tensión": datos["Tensión de punto de medición"],
                    "Transformador del tablero": datos["Transformador del tablero"],
                    "Temporalidad de medición": datos["Temporalidad de medición"],
                    "Fecha de medición inicial": datos["Fecha de medición inicial"],
                    "Fecha de medición final": datos["Fecha de medición final"],
                },
            )

            status.write("Enviando mensaje a la cola de procesamiento...")
            tension_valor, tension_unidad = _extraer_tension_nominal(
                datos["Tensión de punto de medición"]
            )
            if tension_valor is None:
                raise ValueError(
                    "No se pudo extraer la tensión nominal del punto de medición."
                )

            mode = st.secrets["aws"].get("mode", "dev")
            report_base_url = (
                "http://localhost:8501"
                if mode == "dev"
                else st.secrets["aws"].get("report_base_url", "http://localhost:8501")
            )
            skip_llm_value = st.session_state.get("skip_llm", True)
            demand = datos["Demanda Valor"] if datos["Demanda Valor"] is not None else 0.0
            if datos["Tension suministro valor"] is not None:
                supply_voltage = datos["Tension suministro valor"]
                supply_voltage_unit = datos["Tension suministro unidad"]
            else:
                supply_voltage = 0.0
                supply_voltage_unit = ""
            il = (
                datos["Corriente demanda máxima contratada valor"]
                if datos["Corriente demanda máxima contratada valor"] is not None
                else 0.0
            )
            icc = (
                datos["Corriente de corto circuito valor"]
                if datos["Corriente de corto circuito valor"] is not None
                else 0.0
            )
            icc_u = datos["Corriente de corto circuito unidad"]
            il_u = datos["Corriente demanda máxima contratada unidad"]

            mensaje_sqs = build_sqs_message(
                report_id=report_id,
                bucket=bucket,
                region=Servicio.Region,
                input_filenames=input_names,
                email=email_final,
                report_base_url=report_base_url,
                nominal_voltage=tension_valor,
                nominal_voltage_unit=tension_unidad,
                profile=datos["_perfil_tecnico"],
                skip_llm=skip_llm_value,
                enable_cfe_charts=cfe_agregado,
                cfe_file=CFE_FILE_NAME,
                demand=demand,
                demand_unit=datos["Demanda Unidad"],
                supply_voltage=supply_voltage,
                supply_voltage_unit=supply_voltage_unit,
                icc=icc,
                il=il,
                icc_unit=icc_u.value,
                il_unit=il_u.value,
            )
            queue_url = st.secrets["aws"]["sqs_queue_url"]
            Servicio.enviar_mensaje_sqs(queue_url, mensaje_sqs)

            status.update(label="Carga completa", state="complete", expanded=False)
            st.session_state.carga_fase = "complete"
            st.rerun()
        except Exception as e:
            status.update(label="Error crítico", state="error")
            st.error(f"Hubo un error al conectar con AWS: {e}")
            st.session_state.carga_fase = "review"


def _render_email_confirmacion():
    """Panel inline bajo el formulario (no modal ni pantalla aparte)."""
    st.divider()
    st.subheader("Confirmación de envío")
    st.caption("Confirme el correo para el enlace del reporte. Los datos del formulario quedan arriba.")

    email_envio = st.text_input(
        "Correo electrónico para envío del reporte",
        value=st.session_state.get("email_final") or "",
        placeholder="ejemplo@correo.com",
        key="email_envio_carga_inline",
    )
    skip_llm_toggle = st.toggle(
        "Omitir generación de reportes LLM",
        value=st.session_state.skip_llm,
        key="skip_llm_toggle_inline",
        help="Solo tablas y gráficos, sin análisis LLM.",
    )

    snap_modal = st.session_state.get("carga_snapshot") or {}
    arch_modal = snap_modal.get("archivos") or {}
    main_entries = arch_modal.get("main_files") or []
    n_main = len(main_entries) if isinstance(main_entries, list) else (1 if main_entries else 0)
    if n_main >= 2:
        st.info(
            f"Se procesarán **{n_main} archivos de medición** "
            "(concatenación horizontal antes del reporte)."
        )
    if arch_modal.get("CFE") is not None:
        st.warning("Este cliente se procesará con archivo de la CFE.")
    else:
        st.warning("Este cliente se procesará sin archivo de la CFE.")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Confirmar y continuar", type="primary", use_container_width=True, key="btn_email_confirm"):
            if not email_envio or "@" not in email_envio.strip():
                st.session_state.email_confirm_error = "Ingrese un correo electrónico válido."
            else:
                st.session_state.email_confirm_error = None
                st.session_state.email_final = email_envio.strip()
                st.session_state.skip_llm = skip_llm_toggle
                st.session_state.mostrar_modal_email = False
                st.session_state.procesar_carga = True
    with col_btn2:
        if st.button("Cancelar envío", use_container_width=True, key="btn_email_cancel"):
            st.session_state.mostrar_modal_email = False
            st.session_state.email_confirm_error = None
            st.session_state.procesar_carga = False

    if st.session_state.get("email_confirm_error"):
        st.error(st.session_state.email_confirm_error)


def _render_complete_inline():
    st.divider()
    st.subheader("Reporte en cola")
    st.success(f"Archivos recibidos. ID del reporte: `{st.session_state.report_uuid}`")
    if st.session_state.email_final:
        st.info(f"El enlace se enviará a {st.session_state.email_final}")
    if st.button("Nuevo reporte", type="primary", key="btn_nuevo_reporte"):
        _clear_carga_session()
        st.rerun()


def CargarDatos2():
    Servicio = get_servicio_base()
    _init_carga_session()

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
                t_sum = cc1.number_input(label="Tensión Suministro (Valor)",value=None)
                u_sum = cc2.selectbox("U.", ["V", "kV"], key="usum")
                datos_formulario["Tensión de suministro"] = f"{t_sum} {u_sum}" if t_sum else ""
                datos_formulario["Tension suministro valor"]=t_sum
                datos_formulario["Tension suministro unidad"]=u_sum
                # Demanda
                cc1, cc2 = st.columns([0.7, 0.3])
                dem = cc1.number_input("Demanda Contratada (Valor)",value=None)
                u_dem = cc2.selectbox("U.", ["kW", "MW", "W"], key="udem")
                datos_formulario["Demanda contratada"] = f"{dem} {u_dem}" if dem else ""
                datos_formulario["Demanda Valor"]=dem
                datos_formulario["Demanda Unidad"]=u_dem

                # Corriente Demanda
                cc1, cc2 = st.columns([0.7, 0.3])
                i_dem = cc1.number_input("Corriente demanda máx (Valor)", value=None)
                u_idem = cc2.selectbox(
                    "U.",
                    list(CorrienteUnidad),
                    format_func=lambda u: u.value,
                    index=list(CorrienteUnidad).index(CorrienteUnidad.A),
                    key="uidem",
                )
                datos_formulario["Corriente demanda máxima contratada"] = (
                    f"{i_dem} {u_idem.value}" if i_dem else ""
                )
                datos_formulario["Corriente demanda máxima contratada valor"] = i_dem
                datos_formulario["Corriente demanda máxima contratada unidad"] = u_idem
            with col_b:
                datos_formulario["Transformador del tablero"] = st.text_input("Transformador (Capacidad/Tipo)")
                
                # Tensión Punto
                cc1, cc2 = st.columns([0.7, 0.3])
                t_pto = cc1.number_input("Tensión Punto (Valor)",value=None)
                u_pto = cc2.selectbox("U.", ["V", "kV"], key="upto")
                datos_formulario["Tensión de punto de medición"] = f"{t_pto} {u_pto}" if t_pto else ""

                # Corriente CC
                cc1, cc2 = st.columns([0.7, 0.3])
                icc = cc1.number_input("Corriente CC (Valor)", value=None)
                u_icc = cc2.selectbox(
                    "U.",
                    list(CorrienteUnidad),
                    format_func=lambda u: u.value,
                    index=list(CorrienteUnidad).index(CorrienteUnidad.KA),
                    key="uicc",
                )
                datos_formulario["Corriente de corto circuito"] = (
                    f"{icc} {u_icc.value}" if icc else ""
                )
                datos_formulario["Corriente de corto circuito valor"] = icc
                datos_formulario["Corriente de corto circuito unidad"] = u_icc

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
            archivos_formulario["main_files"] = st.file_uploader(
                "Archivos de medición (CSV/PQDIF/XLSX)",
                type=["csv", "pqd", "pqdif", "xlsx"],
                accept_multiple_files=True,
                help="Puede seleccionar uno o varios archivos. Si son 2 o más, se concatenan "
                "antes del chequeo de columnas y del reporte (mismo flujo que input_keys en SQS).",
            )
            with st.expander("📁 Habilitar archivo Comisión Federal de Electricidad (Opcional)"):
                archivos_formulario["CFE"] = st.file_uploader("Archivo Comisión Federal de Electricidad (CSV) (Opcional)", type=["csv", "xlsx"])

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
    # 2. LÓGICA (misma página: secciones debajo del formulario)
    # ==========================================

    if submit_button:
        
        # A. VALIDACIÓN ESTRICTA
        errores = []
        for campo, valor in datos_formulario.items():
            # Ignorar campos internos que empiezan con _
            if campo.startswith("_"):
                continue
            if not valor or str(valor).strip() == "": errores.append(campo)
        
        for nombre_archivo, objeto_archivo in archivos_formulario.items():
            if nombre_archivo == "CFE":
                continue
            if nombre_archivo == "main_files":
                if not objeto_archivo:
                    errores.append("Archivos de medición")
                continue
            if objeto_archivo is None:
                errores.append(nombre_archivo)

        if errores:
            st.error(f"❌ Faltan los siguientes campos obligatorios: {', '.join(errores)}")
            return

        st.session_state.carga_snapshot = _serialize_form_snapshot(
            datos_formulario, archivos_formulario
        )

        if st.session_state.report_uuid and st.session_state.email_final:
            st.session_state.procesar_carga = True
            st.session_state.mostrar_modal_email = False
        else:
            st.session_state.mostrar_modal_email = True
            st.session_state.procesar_carga = False

    if st.session_state.mostrar_modal_email and not st.session_state.procesar_carga:
        _render_email_confirmacion()

    if st.session_state.procesar_carga:
        _run_upload_raw_only(Servicio)

    if st.session_state.carga_fase == "checking_columns":
        _run_column_check_only(Servicio)

    if st.session_state.carga_fase == "upload_rest":
        _run_upload_rest_and_sqs(Servicio)

    if st.session_state.carga_fase == "review" and st.session_state.column_check_result:
        from cargaDatos.column_check_ui import render_column_check_review

        with st.container(border=True):
            render_column_check_review(st.session_state.column_check_result, embedded=True)

    if st.session_state.carga_fase == "complete":
        _render_complete_inline()