import logging
import streamlit as st
from urllib.parse import urlparse
from Servicio import Data

logger = logging.getLogger("innovapq.generar_archivos_pdf")

# Credenciales: st.secrets ← `.streamlit/secrets.toml` (o STREAMLIT_SECRETS_FILE).


@st.cache_resource
def get_servicio_aws(report_id, _version=1):
    print("Conectando a AWS...")
    return Data(report_id)


@st.cache_data
def get_diccionario_rutas(_Servicio, nombre_carpeta):
    print("Escaneando bucket...")
    return _Servicio.obtener_rutas_actualizadas()


def modal_generacion_pdf_unificado(report_id, servicio, datos_rutas, cfe):
    if "mostrar_modal_pdf" not in st.session_state:
        st.session_state.mostrar_modal_pdf = False
    if "pdf_enviado" not in st.session_state:
        st.session_state.pdf_enviado = False
    if "email_pdf_enviado" not in st.session_state:
        st.session_state.email_pdf_enviado = ""

    if st.session_state.pdf_enviado:
        st.success(
            f"✅ **Solicitud enviada a la cola PDF**\n\n"
            f"Correo indicado: **{st.session_state.email_pdf_enviado}**\n\n"
            f"📬 Recibirá el correo cuando el pipeline termine."
        )
        if st.button("Cerrar", key="cerrar_mensaje_pdf_global"):
            st.session_state.pdf_enviado = False
            st.session_state.email_pdf_enviado = ""
            st.rerun()
        return

    if not st.session_state.pdf_enviado:
        if st.button("Generar .ZIP de todos los reportes", use_container_width=True, type="primary"):
            st.session_state.mostrar_modal_pdf = True
            st.rerun()

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
                help="Seleccione la fecha que aparecerá en los reportes PDF",
            )

            st.divider()

            opciones_reportes = {
                "Reporte de código red": "codigo_red",
                "Reporte PQ": "pq",
                "Reporte de energía": "energia",
            }

            st.write("Selecciona los reportes a generar:")

            report_types = []
            for texto_mostrar, valor_guardar in opciones_reportes.items():
                if st.checkbox(
                    texto_mostrar,
                    value=False,
                    key=f"pdf_modal_rt_{valor_guardar}",
                ):
                    report_types.append(valor_guardar)

            st.divider()

            enable_cfe = False
            if cfe == "true":
                st.write("Seleccione para habilitar el reporte del CFE:")
                enable_cfe = st.checkbox(
                    "Habilitar gráficas CFE",
                    value=True,
                )
            else:
                st.write("Reporte del CFE no disponible para este cliente.")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                enviar_btn = st.form_submit_button("✅ Enviar Todo", use_container_width=True, type="primary")
            with col_btn2:
                cancelar_btn = st.form_submit_button("❌ Cancelar", use_container_width=True)

            if cancelar_btn:
                st.session_state.mostrar_modal_pdf = False
                st.rerun()

            if enviar_btn:
                if not email_pdf or "@" not in email_pdf:
                    st.error("Por favor, ingrese un correo electrónico válido.")
                elif fecha_reporte is None:
                    st.error("Por favor, seleccione la fecha del reporte.")
                elif len(report_types) == 0:
                    st.error("Seleccione al menos un tipo de reporte para continuar.")
                else:
                    try:
                        tipo_a_clave_ruta = {
                            "codigo_red": "CodigoRed",
                            "energia": "Energia",
                            "pq": "PQ",
                        }

                        with st.spinner("Comprobando S3, sincronizando comentarios si hay edición local y enviando a SQS…"):
                            for rt in report_types:
                                clave = tipo_a_clave_ruta[rt]
                                ruta_s3 = datos_rutas.get(clave)
                                msg_base = f"[PDF pipeline] tipo={rt} key_s3={ruta_s3!r}"

                                if not ruta_s3:
                                    w = (
                                        f"No hay ruta resuelta en el mapa para «{rt}» "
                                        "(el JSON de comentarios no aparece en el inventario S3 de este reporte)."
                                    )
                                    logger.warning("%s — sin ruta en mapa", msg_base)
                                    print(f"{msg_base} — sin ruta en mapa (se envía SQS igual)")
                                    st.warning(w + " Se enviará la solicitud a la cola de todas formas.")
                                    continue

                                existe = servicio.objeto_existe_s3(ruta_s3)
                                logger.info("%s existe_en_s3=%s", msg_base, existe)
                                print(f"{msg_base} existe_en_s3={existe}")

                                if not existe:
                                    st.warning(
                                        f"No existe aún el objeto de comentarios en S3 para «{rt}» "
                                        f"(`{ruta_s3}`). Se enviará la solicitud a la cola de todas formas."
                                    )

                                json_key = f"comentarios_json_{ruta_s3}"
                                if json_key in st.session_state:
                                    logger.info(
                                        "%s guardando borrador desde sesión → S3", msg_base
                                    )
                                    print(f"{msg_base} GuardarDatos desde session_state")
                                    servicio.GuardarDatos(
                                        st.session_state[json_key], ruta_s3
                                    )

                            fecha_formato = fecha_reporte.strftime("%Y-%m-%d")
                            mensaje_pdf_sqs = {
                                "report_id": report_id,
                                "bucket": servicio.bucket,
                                "region": servicio.Region,
                                "report_types": report_types,
                                "email": email_pdf.strip(),
                                "report_date": fecha_formato,
                                "enable_cfe_charts": enable_cfe,
                            }

                            queue_url_pdf = st.secrets["aws"]["sqs_pdf_queue_url"]
                            logger.info(
                                "Enviando SQS PDF queue_host=%s report_id=%s types=%s",
                                urlparse(queue_url_pdf).netloc,
                                report_id,
                                report_types,
                            )
                            print(
                                f"[PDF pipeline] SQS send report_id={report_id!r} "
                                f"types={report_types} queue={urlparse(queue_url_pdf).netloc}"
                            )

                            resp_sqs = servicio.enviar_mensaje_sqs(
                                queue_url_pdf, mensaje_pdf_sqs
                            )
                            mid = (resp_sqs or {}).get("MessageId", "")
                            logger.info("SQS enviado MessageId=%s", mid)
                            print(f"[PDF pipeline] SQS enviado MessageId={mid}")

                        st.session_state.mostrar_modal_pdf = False
                        st.session_state.pdf_enviado = True
                        st.session_state.email_pdf_enviado = email_pdf.strip()
                        st.rerun()

                    except Exception as e:
                        logger.exception("Error enviando PDF pipeline: %s", e)
                        print(f"[PDF pipeline] ERROR: {e}")
                        st.error(f"❌ Error al procesar la solicitud: {str(e)}")


def GenerarArchivos(report_id, cfe):
    if not report_id or str(report_id).strip() == "":
        st.error(
            "Falta `report_id` en la URL. Ejemplo: `?report_id=reportTU_UUID&pagina=reporte`"
        )
        return

    Servicio = get_servicio_aws(report_id, _version=1)
    Datos = get_diccionario_rutas(_Servicio=Servicio, nombre_carpeta=report_id)

    st.header("📁 Gestión de Archivos y Reportes")

    modal_generacion_pdf_unificado(
        report_id=report_id,
        servicio=Servicio,
        datos_rutas=Datos["Comentarios"],
        cfe=cfe,
    )
