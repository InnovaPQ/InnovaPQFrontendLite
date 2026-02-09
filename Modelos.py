import openpyxl
import pandas as pd
import streamlit as st
import json
# --- Clases ---

class Tabla:
    def __init__(self,titulo,rutaDatos,servicio):
        self.titulo=titulo
        self.rutaDatos=rutaDatos
        self.servicio=servicio

    def construirContenedor(self):
        df=self.servicio.descargar_archivo_s3(self.rutaDatos)
        if df is None:
            st.error("No se encontraron datos para esta Tabla.")
            return
        st.subheader(self.titulo)
        st.table(data=df)

class Descripciones:
    def __init__(self,rutaDatos,servicio):
        self.rutaDatos=rutaDatos
        self.servicio=servicio
    
    def ConstruirContenedor(self):
        df=self.servicio.descargar_archivo_s3(self.rutaDatos)
        try:
            for index,row in df.iterrows():
                with st.container():
                    col1,col2=st.columns([0.3,0.7])
                    with col1:
                        st.markdown(
                            f'<p style="font-size: 18px; font-weight: bold;color:black;">{str(row[0])} </p>',
                            unsafe_allow_html=True
                            )
                    with col2:
                        st.write(str(row[1]))
        except Exception as e:
            st.error(f"Error al construir descripciones. Revisa el ID del reporte.")
                
class Imagenes:
    def __init__(self,titulo,rutaDatos,servicio):
        self.rutaDatos=rutaDatos
        self.titulo=titulo
        self.servicio=servicio
    def ConstruirImagen(self):
        captionImg=st.markdown(
                f'<p style="font-size: 18px; font-weight: bold;color:black;">{self.titulo} </p>',
                unsafe_allow_html=True
                )
        col1, col2, col3 = st.columns([0.1,0.8,0.1])
        with col2:
            imagen=self.servicio.descargar_archivo_s3(self.rutaDatos)
            if not imagen:
                st.error("No se pudo cargar el archivo de Imagen.")
                return
            st.image(image=imagen) 
    

class Comentarios:
    def __init__(self, titulo, seccion_json, rutaDatos, servicio):
        """
        Args:
            titulo_ui (str): El título que aparecerá arriba del text_area (ej: "Notas Técnicas").
            seccion_json (str): La llave del JSON a leer (ej: 'nota', 'importante', 'executive_summary').
            ruta_archivo_s3 (str): La ruta completa en S3 donde está este JSON de reporte.
            servicio_datos (Data): La instancia de tu servicio de conexión.
        """
        self.titulo_ui = titulo
        self.seccion_json = seccion_json
        self.ruta_archivo_s3 = rutaDatos
        self.servicio = servicio

    def render(self):
        # 1. Mostrar el título en la UI
        st.subheader(self.titulo_ui)

        # 2. Cargar JSON completo una vez y guardarlo en session_state
        json_key = f"comentarios_json_{self.ruta_archivo_s3}"
        if json_key not in st.session_state:
            bytes_data = self.servicio.descargar_archivo_s3(self.ruta_archivo_s3)
            
            if not bytes_data:
                st.error("No se pudo cargar el archivo de comentarios.")
                return None
            
            try:
                data_dict = json.loads(bytes_data.decode('utf-8'))
                st.session_state[json_key] = data_dict
                st.session_state[f"ruta_comentarios_{self.ruta_archivo_s3}"] = self.ruta_archivo_s3
            except json.JSONDecodeError:
                st.error("El archivo descargado no tiene un formato JSON válido.")
                return None
            except Exception as e:
                st.error(f"Error procesando comentarios: {e}")
                return None
        
        # 3. Obtener el JSON completo del session_state
        data_dict = st.session_state[json_key]
        
        # 4. Extraer la sección solicitada
        contenido_raw = data_dict.get(self.seccion_json, None)

        if contenido_raw is None:
            st.warning(f"No se encontró la sección '{self.seccion_json}' en el reporte.")
            return None

        # 5. Si es una lista (nota, importante, precaucion), renderizar items individuales
        if isinstance(contenido_raw, list):
            items_editados = []
            
            # Renderizar cada item individualmente
            for idx, item in enumerate(contenido_raw):
                with st.container():
                    # Mostrar el título como referencia (solo lectura)
                    titulo_original = item.get('title', f'Item {idx + 1}')
                    st.caption(f"📝 {titulo_original}")
                    
                    # Text area para editar solo el content
                    content_key = f"{self.seccion_json}_content_{idx}"
                    content_editado = st.text_area(
                        label=f"Contenido del item {idx + 1}",
                        value=item.get('content', ''),
                        height=150,
                        key=content_key,
                        label_visibility="collapsed"
                    )
                    
                    # Botón para eliminar (solo si hay más de 1 item)
                    if len(contenido_raw) > 1:
                        button_key = f"delete_{self.seccion_json}_{idx}"
                        # Estilo CSS para hacer el botón rojo
                        st.markdown(f"""
                            <style>
                                button[data-testid*="{button_key}"] {{
                                    background-color: #ff4444 !important;
                                    color: white !important;
                                    border-color: #cc0000 !important;
                                }}
                                button[data-testid*="{button_key}"]:hover {{
                                    background-color: #cc0000 !important;
                                }}
                            </style>
                        """, unsafe_allow_html=True)
                        
                        if st.button("Eliminar", key=button_key, 
                                   type="secondary", use_container_width=True,
                                   help="Eliminar esta nota"):
                            # Eliminar el item de la lista
                            contenido_raw.pop(idx)
                            st.session_state[json_key][self.seccion_json] = contenido_raw
                            st.rerun()
                    
                    # Guardar el item editado
                    item_editado = item.copy()
                    item_editado['content'] = content_editado
                    items_editados.append(item_editado)
                
                st.divider()
            
            # Actualizar el JSON en session_state con los cambios
            data_dict[self.seccion_json] = items_editados
            st.session_state[json_key] = data_dict
            
            # Botón para agregar nueva nota
            if st.button(f"➕ Agregar nueva {self.seccion_json}", key=f"add_{self.seccion_json}"):
                nuevo_item = {
                    "title": f"Nueva {self.seccion_json}",
                    "content": "",
                    "priority": self.seccion_json,
                    "references": []
                }
                contenido_raw.append(nuevo_item)
                st.session_state[json_key][self.seccion_json] = contenido_raw
                st.rerun()
            
            # Retornar el JSON completo actualizado
            return st.session_state[json_key]
        
        # 6. Si es texto plano (executive_summary, technical_summary)
        elif isinstance(contenido_raw, str):
            texto_key = f"{self.seccion_json}_text"
            texto_editado = st.text_area(
                label="",
                value=contenido_raw,
                height=500,
                key=texto_key,
                label_visibility="collapsed"
            )
            # Actualizar en session_state
            data_dict[self.seccion_json] = texto_editado
            st.session_state[json_key] = data_dict
            return st.session_state[json_key]
        
        else:
            st.warning(f"Tipo de contenido no soportado para edición: {type(contenido_raw)}")
            return None