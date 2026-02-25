#--------------------------CodigoRed-------------
# # Inicializar estado del modal
# if 'mostrar_modal_pdf' not in st.session_state:
# st.session_state.mostrar_modal_pdf = False
# if 'pdf_enviado' not in st.session_state:
# st.session_state.pdf_enviado = False
# if 'email_pdf_enviado' not in st.session_state:
# st.session_state.email_pdf_enviado = ""

# # Mostrar mensaje de éxito si ya se envió
# if st.session_state.pdf_enviado:
# st.success(f"✅ **Solicitud enviada**\n\n"
# f"PDF será enviado a:\n"
# f"**{st.session_state.email_pdf_enviado}**\n\n"
# f"📬 Recibirá el correo en los próximos minutos.")
# if st.button("Cerrar", key="cerrar_mensaje_pdf"):
# st.session_state.pdf_enviado = False
# st.session_state.email_pdf_enviado = ""
# st.rerun()

# # Botón para abrir modal
# if not st.session_state.pdf_enviado:
# if st.button("Generar PDF con comentarios actualizados", use_container_width=True,key=f"{report_id}_CodigoRed"):
# st.session_state.mostrar_modal_pdf = True
# st.rerun()

# # Modal para solicitar email y fecha
# if st.session_state.mostrar_modal_pdf and not st.session_state.pdf_enviado:
# st.info("📧 Ingrese el correo y la fecha del reporte para enviar el PDF.")

# with st.form(key="form_modal_pdf", clear_on_submit=False):
# email_pdf = st.text_input(
# "Correo Electrónico",
# placeholder="ejemplo@correo.com",
# type="default"
# )

# fecha_reporte = st.date_input(
# "Fecha del Reporte",
# value=None,
# help="Seleccione la fecha que aparecerá en el reporte PDF"
# )

# col_btn1, col_btn2 = st.columns(2)
# with col_btn1:
# enviar_btn = st.form_submit_button("✅ Enviar", use_container_width=True, type="primary")
# with col_btn2:
# cancelar_btn = st.form_submit_button("❌ Cancelar", use_container_width=True)

# if cancelar_btn:
# st.session_state.mostrar_modal_pdf = False
# st.rerun()

# if enviar_btn:
# # Validar email
# if not email_pdf or email_pdf.strip() == "":
#     st.error("Por favor, ingrese un correo electrónico válido.")
# elif "@" not in email_pdf:
#     st.error("Por favor, ingrese un correo electrónico válido.")
# elif fecha_reporte is None:
#     st.error("Por favor, seleccione la fecha del reporte.")
# else:
#     try:
#         # Validar que hay al menos 1 item en cada sección
#         if json_key not in st.session_state:
#             st.error("No se encontraron comentarios para guardar. Por favor, recargue la página.")
#         else:
#             json_para_guardar = st.session_state[json_key]
            
#             # Validar que solo la sección "nota" tenga al menos 1 item
#             # "importante" y "precaución" son opcionales según los prompts del LLM
#             errores_validacion = []
            
#             # Solo validar "nota" como requerida
#             contenido_nota = json_para_guardar.get("nota", [])
#             if not isinstance(contenido_nota, list) or len(contenido_nota) == 0:
#                 errores_validacion.append(f"La sección 'nota' debe tener al menos un item.")
            
#             if errores_validacion:
#                 st.error("❌ " + " ".join(errores_validacion))
#             else:
#                 # Verificar que las variables estén disponibles
#                 if not rutaComentarios:
#                     st.error("No se pudo obtener la ruta de comentarios.")
#                 elif not json_para_guardar:
#                     st.error("No hay datos de comentarios para guardar.")
#                 else:
#                     # Guardar comentarios actualizados en S3
#                     Servicio.GuardarDatos(
#                         json_para_guardar,
#                         rutaComentarios
#                     )
                    
#                     # Construir mensaje para SQS PDF
#                     # Convertir fecha a formato YYYY-MM-DD
#                     fecha_formato = fecha_reporte.strftime("%Y-%m-%d")
                    
#                     mensaje_pdf_sqs = {
#                         "report_id": report_id,
#                         "bucket": Servicio.bucket,
#                         "region": Servicio.Region,
#                         "report_type": "codigo_red",
#                         "email": email_pdf.strip(),
#                         "report_date": fecha_formato
#                     }
                    
#                     # Obtener URL de la cola PDF desde secrets
#                     queue_url_pdf = st.secrets["aws"]["sqs_pdf_queue_url"]
                    
#                     # Enviar mensaje a SQS
#                     Servicio.enviar_mensaje_sqs(queue_url_pdf, mensaje_pdf_sqs)
                    
#                     # Cerrar modal y marcar como enviado
#                     st.session_state.mostrar_modal_pdf = False
#                     st.session_state.pdf_enviado = True
#                     st.session_state.email_pdf_enviado = email_pdf.strip()
#                     st.rerun()
#     except Exception as e:
#         st.error(f"❌ Error al enviar la solicitud: {str(e)}\n\nPor favor, intente nuevamente.")


#--------------------Energia--------------------

# # Inicializar estado del modal
#         if 'mostrar_modal_pdf' not in st.session_state:
#             st.session_state.mostrar_modal_pdf = False
#         if 'pdf_enviado' not in st.session_state:
#             st.session_state.pdf_enviado = False
#         if 'email_pdf_enviado' not in st.session_state:
#             st.session_state.email_pdf_enviado = ""
        
#         # Mostrar mensaje de éxito si ya se envió
#         if st.session_state.pdf_enviado:
#             st.success(f"✅ **Solicitud enviada**\n\n"
#                       f"PDF será enviado a:\n"
#                       f"**{st.session_state.email_pdf_enviado}**\n\n"
#                       f"📬 Recibirá el correo en los próximos minutos.")
#             if st.button("Cerrar", key="cerrar_mensaje_pdf_energia"):
#                 st.session_state.pdf_enviado = False
#                 st.session_state.email_pdf_enviado = ""
#                 st.rerun()
        
#         # Botón para abrir modal
#         if not st.session_state.pdf_enviado:
#             if st.button("Generar PDF con comentarios actualizados", use_container_width=True,key=f"{report_id}_Energia"):
#                 st.session_state.mostrar_modal_pdf = True
#                 st.rerun()
        
#         # Modal para solicitar email
#         if st.session_state.mostrar_modal_pdf and not st.session_state.pdf_enviado:
#             st.info("📧 Ingrese el correo y la fecha del reporte para enviar el PDF.")
            
#             with st.form(key="form_modal_pdf", clear_on_submit=False):
#                 email_pdf = st.text_input(
#                     "Correo Electrónico",
#                     placeholder="ejemplo@correo.com",
#                     type="default"
#                 )
                
#                 fecha_reporte = st.date_input(
#                     "Fecha del Reporte",
#                     value=None,
#                     help="Seleccione la fecha que aparecerá en el reporte PDF"
#                 )
                
#                 col_btn1, col_btn2 = st.columns(2)
#                 with col_btn1:
#                     enviar_btn = st.form_submit_button("✅ Enviar", use_container_width=True, type="primary")
#                 with col_btn2:
#                     cancelar_btn = st.form_submit_button("❌ Cancelar", use_container_width=True)
                
#                 if cancelar_btn:
#                     st.session_state.mostrar_modal_pdf = False
#                     st.rerun()
                
#                 if enviar_btn:
#                     # Validar email
#                     if not email_pdf or email_pdf.strip() == "":
#                         st.error("Por favor, ingrese un correo electrónico válido.")
#                     elif "@" not in email_pdf:
#                         st.error("Por favor, ingrese un correo electrónico válido.")
#                     elif fecha_reporte is None:
#                         st.error("Por favor, seleccione la fecha del reporte.")
#                     else:
#                         try:
#                             # Validar que hay al menos 1 item en cada sección
#                             if json_key not in st.session_state:
#                                 st.error("No se encontraron comentarios para guardar. Por favor, recargue la página.")
#                             else:
#                                 json_para_guardar = st.session_state[json_key]
                                
#                                 # Validar que solo la sección "nota" tenga al menos 1 item
#                                 # "importante" y "precaución" son opcionales según los prompts del LLM
#                                 errores_validacion = []
                                
#                                 # Solo validar "nota" como requerida
#                                 contenido_nota = json_para_guardar.get("nota", [])
#                                 if not isinstance(contenido_nota, list) or len(contenido_nota) == 0:
#                                     errores_validacion.append(f"La sección 'nota' debe tener al menos un item.")
                                
#                                 if errores_validacion:
#                                     st.error("❌ " + " ".join(errores_validacion))
#                                 else:
#                                     # Verificar que las variables estén disponibles
#                                     if not rutaComentarios:
#                                         st.error("No se pudo obtener la ruta de comentarios.")
#                                     elif not json_para_guardar:
#                                         st.error("No hay datos de comentarios para guardar.")
#                                     else:
#                                         # Guardar comentarios actualizados en S3
#                                         Servicio.GuardarDatos(
#                                             json_para_guardar,
#                                             rutaComentarios
#                                         )
                                        
#                                         # Construir mensaje para SQS PDF
#                                         # Convertir fecha a formato YYYY-MM-DD
#                                         fecha_formato = fecha_reporte.strftime("%Y-%m-%d")
                                        
#                                         mensaje_pdf_sqs = {
#                                             "report_id": report_id,
#                                             "bucket": Servicio.bucket,
#                                             "region": Servicio.Region,
#                                             "report_type": "energia",
#                                             "email": email_pdf.strip(),
#                                             "report_date": fecha_formato
#                                         }
                                        
#                                         # Obtener URL de la cola PDF desde secrets
#                                         queue_url_pdf = st.secrets["aws"]["sqs_pdf_queue_url"]
                                        
#                                         # Enviar mensaje a SQS
#                                         Servicio.enviar_mensaje_sqs(queue_url_pdf, mensaje_pdf_sqs)
                                        
#                                         # Cerrar modal y marcar como enviado
#                                         st.session_state.mostrar_modal_pdf = False
#                                         st.session_state.pdf_enviado = True
#                                         st.session_state.email_pdf_enviado = email_pdf.strip()
#                                         st.rerun()
#                         except Exception as e:
#                             st.error(f"❌ Error al enviar la solicitud: {str(e)}\n\nPor favor, intente nuevamente.")


#---------------------------Codigo Red-----------------------
       # Inicializar estado del modal
        # if 'mostrar_modal_pdf' not in st.session_state:
        #     st.session_state.mostrar_modal_pdf = False
        # if 'pdf_enviado' not in st.session_state:
        #     st.session_state.pdf_enviado = False
        # if 'email_pdf_enviado' not in st.session_state:
        #     st.session_state.email_pdf_enviado = ""
        
        # # Mostrar mensaje de éxito si ya se envió
        # if st.session_state.pdf_enviado:
        #     st.success(f"✅ **Solicitud enviada**\n\n"
        #               f"PDF será enviado a:\n"
        #               f"**{st.session_state.email_pdf_enviado}**\n\n"
        #               f"📬 Recibirá el correo en los próximos minutos.")
        #     if st.button("Cerrar", key="cerrar_mensaje_pdf_pq"):
        #         st.session_state.pdf_enviado = False
        #         st.session_state.email_pdf_enviado = ""
        #         st.rerun()
        
        # # Botón para abrir modal
        # if not st.session_state.pdf_enviado:
        #     if st.button("Generar PDF con comentarios actualizados", use_container_width=True,key=f"{report_id}_PQ"):
        #         st.session_state.mostrar_modal_pdf = True
        #         st.rerun()
        
        # # Modal para solicitar email y fecha
        # if st.session_state.mostrar_modal_pdf and not st.session_state.pdf_enviado:
        #     st.info("📧 Ingrese el correo y la fecha del reporte para enviar el PDF.")
            
        #     with st.form(key="form_modal_pdf", clear_on_submit=False):
        #         email_pdf = st.text_input(
        #             "Correo Electrónico",
        #             placeholder="ejemplo@correo.com",
        #             type="default"
        #         )
                
        #         fecha_reporte = st.date_input(
        #             "Fecha del Reporte",
        #             value=None,
        #             help="Seleccione la fecha que aparecerá en el reporte PDF"
        #         )
                
        #         col_btn1, col_btn2 = st.columns(2)
        #         with col_btn1:
        #             enviar_btn = st.form_submit_button("✅ Enviar", use_container_width=True, type="primary")
        #         with col_btn2:
        #             cancelar_btn = st.form_submit_button("❌ Cancelar", use_container_width=True)
                
        #         if cancelar_btn:
        #             st.session_state.mostrar_modal_pdf = False
        #             st.rerun()
                
        #         if enviar_btn:
        #             # Validar email
        #             if not email_pdf or email_pdf.strip() == "":
        #                 st.error("Por favor, ingrese un correo electrónico válido.")
        #             elif "@" not in email_pdf:
        #                 st.error("Por favor, ingrese un correo electrónico válido.")
        #             elif fecha_reporte is None:
        #                 st.error("Por favor, seleccione la fecha del reporte.")
        #             else:
        #                 try:
        #                     # Validar que hay al menos 1 item en cada sección
        #                     if json_key not in st.session_state:
        #                         st.error("No se encontraron comentarios para guardar. Por favor, recargue la página.")
        #                     else:
        #                         json_para_guardar = st.session_state[json_key]
                                
        #                         # Validar que solo la sección "nota" tenga al menos 1 item
        #                         # "importante" y "precaución" son opcionales según los prompts del LLM
        #                         errores_validacion = []
                                
        #                         # Solo validar "nota" como requerida
        #                         contenido_nota = json_para_guardar.get("nota", [])
        #                         if not isinstance(contenido_nota, list) or len(contenido_nota) == 0:
        #                             errores_validacion.append(f"La sección 'nota' debe tener al menos un item.")
                                
        #                         if errores_validacion:
        #                             st.error("❌ " + " ".join(errores_validacion))
        #                         else:
        #                             # Verificar que las variables estén disponibles
        #                             if not rutaComentarios:
        #                                 st.error("No se pudo obtener la ruta de comentarios.")
        #                             elif not json_para_guardar:
        #                                 st.error("No hay datos de comentarios para guardar.")
        #                             else:
        #                                 # Guardar comentarios actualizados en S3
        #                                 Servicio.GuardarDatos(
        #                                     json_para_guardar,
        #                                     rutaComentarios
        #                                 )
                                        
        #                                 # Construir mensaje para SQS PDF
        #                                 # Convertir fecha a formato YYYY-MM-DD
        #                                 fecha_formato = fecha_reporte.strftime("%Y-%m-%d")
                                        
        #                                 mensaje_pdf_sqs = {
        #                                     "report_id": report_id,
        #                                     "bucket": Servicio.bucket,
        #                                     "region": Servicio.Region,
        #                                     "report_type": "pq",
        #                                     "email": email_pdf.strip(),
        #                                     "report_date": fecha_formato
        #                                 }
                                        
        #                                 # Validar que el mensaje tenga todos los campos requeridos
        #                                 campos_requeridos = ["report_id", "bucket", "region", "report_type", "email", "report_date"]
        #                                 campos_faltantes = [campo for campo in campos_requeridos if not mensaje_pdf_sqs.get(campo)]
                                        
        #                                 if campos_faltantes:
        #                                     st.error(f"❌ Faltan campos requeridos en el mensaje: {', '.join(campos_faltantes)}")
        #                                 else:
        #                                     # Obtener URL de la cola PDF desde secrets
        #                                     queue_url_pdf = st.secrets["aws"]["sqs_pdf_queue_url"]
                                            
        #                                     if not queue_url_pdf:
        #                                         st.error("❌ No se encontró la URL de la cola SQS en los secrets. Verifique la configuración.")
        #                                     else:
        #                                         # Enviar mensaje a SQS
        #                                         try:
        #                                             Servicio.enviar_mensaje_sqs(queue_url_pdf, mensaje_pdf_sqs)
        #                                             st.success(f"✅ Mensaje enviado correctamente a SQS para generar PDF")
                                                    
        #                                             # Cerrar modal y marcar como enviado SOLO si el envío fue exitoso
        #                                             st.session_state.mostrar_modal_pdf = False
        #                                             st.session_state.pdf_enviado = True
        #                                             st.session_state.email_pdf_enviado = email_pdf.strip()
        #                                             st.rerun()
        #                                         except Exception as sqs_error:
        #                                             st.error(f"❌ Error al enviar mensaje a SQS: {str(sqs_error)}")
        #                                             raise sqs_error
        #                 except Exception as e:
        #                     st.error(f"❌ Error al enviar la solicitud: {str(e)}\n\nPor favor, intente nuevamente.")
