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


# =============================================================================
# CLASE: TablaEditable
# Extiende la clase base Tabla para permitir edición interactiva de datos
# almacenados en S3, usando el componente data_editor de Streamlit.
# =============================================================================

class TablaEditable(Tabla):

    # -------------------------------------------------------------------------
    # INICIALIZACIÓN
    # -------------------------------------------------------------------------

    def __init__(self, titulo: str, rutaDatos: str, servicio):
        """
        Inicializa la tabla editable heredando de la clase base Tabla.

        Genera claves únicas en session_state para aislar el estado
        de cada instancia de tabla dentro de la misma sesión de Streamlit.

        Args:
            titulo    (str): Nombre visible de la tabla.
            rutaDatos (str): Ruta del archivo en S3.
            servicio       : Objeto con métodos para interactuar con S3.
        """
        super().__init__(titulo, rutaDatos, servicio)

        # Claves únicas en session_state para esta tabla específica
        self.key_datos        = f"datos_{self.titulo}"
        self.key_modo_edicion = f"modo_edicion_{self.titulo}"

    # -------------------------------------------------------------------------
    # MÉTODO PRINCIPAL: construir la UI de la tabla
    # -------------------------------------------------------------------------

    def construirContenedor(self):
        """
        Punto de entrada principal para renderizar la tabla.

        Flujo:
            1. Carga los datos desde S3 (solo la primera vez).
            2. Inicializa el estado de edición si no existe.
            3. Renderiza en modo lectura o modo edición según el estado.
        """

        # -- Paso 1: Cargar datos desde S3 si aún no están en sesión ----------
        if self.key_datos not in st.session_state:
            df = self.servicio.descargar_archivo_s3(self.rutaDatos)

            if df is None:
                st.error("No se encontraron datos para esta Tabla.")
                return

            st.session_state[self.key_datos] = df

        # -- Paso 2: Inicializar el modo de edición (False = solo lectura) ----
        if self.key_modo_edicion not in st.session_state:
            st.session_state[self.key_modo_edicion] = False

        # -- Paso 3: Renderizar según el modo activo --------------------------
        st.subheader(self.titulo)

        if st.session_state[self.key_modo_edicion]:
            self._renderizar_modo_edicion()
        else:
            self._renderizar_modo_lectura()

    # -------------------------------------------------------------------------
    # RENDERIZADO: Modo lectura (tabla estática)
    # -------------------------------------------------------------------------

    def _renderizar_modo_lectura(self):
        """
        Muestra los datos como tabla estática y un botón para activar la edición.
        """
        st.table(data=st.session_state[self.key_datos])

        if st.button("Editar Tabla", key=f"btn_editar_{self.titulo}",type="primary"):
            st.session_state[self.key_modo_edicion] = True
            st.rerun()

    # -------------------------------------------------------------------------
    # RENDERIZADO: Modo edición (tabla interactiva)
    # -------------------------------------------------------------------------

    def _renderizar_modo_edicion(self):
        """
        Muestra el editor interactivo de datos con opciones para
        guardar los cambios en S3 o cancelar la edición.
        """
        st.info("Modificando datos. Presiona 'Guardar' para enviar los cambios a S3.")

        # Editor interactivo: permite modificar, agregar y eliminar filas
        df_editado = st.data_editor(
            st.session_state[self.key_datos],
            key=f"editor_{self.titulo}",
            num_rows="dynamic",  # Habilita agregar/borrar filas
        )

        # Creamos un contenedor horizontal
        with st.container(horizontal=True):
            
            # Ambos botones se colocan uno al lado del otro naturalmente
            if st.button("Guardar cambios", type="primary", key=f"btn_guardar_{self.titulo}"):
                self._guardar_en_s3(df_editado)
                
            if st.button("Cancelar", key=f"btn_cancelar_{self.titulo}"):
                self._cancelar_edicion()

# La 'col_vacia' no se usa, simplemente empuja los botones hacia la izquierda

    # -------------------------------------------------------------------------
    # ACCIONES: Guardar y Cancelar
    # -------------------------------------------------------------------------

    def _guardar_en_s3(self, df_editado):
        """
        Sube el DataFrame editado a S3 y actualiza el estado de la sesión.

        Si la operación falla, muestra un mensaje de error sin modificar
        el estado local.

        Args:
            df_editado: DataFrame con los cambios realizados por el usuario.
        """
        exito = self.servicio.actualizar_archivo_s3(self.rutaDatos, df_editado)

        if exito:
            st.success("¡Datos actualizados en S3 correctamente!")

            # Sincronizar caché local con los datos recién guardados
            st.session_state[self.key_datos]        = df_editado
            st.session_state[self.key_modo_edicion] = False
            st.rerun()
        else:
            st.error("Hubo un error al actualizar los datos en S3.")

    def _cancelar_edicion(self):
        """
        Descarta los cambios y regresa al modo de solo lectura.
        """
        st.session_state[self.key_modo_edicion] = False
        st.rerun()

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
                            f'<p style="font-size: 18px; font-weight: bold;color:black;">{str(row.iloc[0])} </p>',
                            unsafe_allow_html=True
                            )
                    with col2:
                        st.write(str(row.iloc[1]))
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
    def __init__(self, titulo, seccion_json, rutaDatos, servicio, id_categoria):
        self.titulo_ui = titulo
        self.seccion_json = seccion_json
        self.ruta_archivo_s3 = rutaDatos
        self.servicio = servicio
        self.id_categoria = id_categoria
        
        # Claves únicas centralizadas
        # Clave maestra para el JSON completo de este archivo
        self.json_key = f"comentarios_json_{self.ruta_archivo_s3}"
        # Prefijo para garantizar que los widgets de esta instancia no colisionen
        self.widget_prefix = f"wg_{self.id_categoria}_{self.seccion_json}"

    def _cargar_datos(self):
        """Descarga y almacena el JSON en session_state una sola vez."""
        if self.json_key not in st.session_state:
            bytes_data = self.servicio.descargar_archivo_s3(self.ruta_archivo_s3)
            
            if not bytes_data:
                st.error("No se pudo cargar el archivo de comentarios.")
                return False
            
            try:
                data_dict = json.loads(bytes_data.decode('utf-8'))
                st.session_state[self.json_key] = data_dict
                st.session_state[f"ruta_comentarios_{self.ruta_archivo_s3}"] = self.ruta_archivo_s3
                return True
            except json.JSONDecodeError:
                st.error("El archivo descargado no tiene un formato JSON válido.")
                return False
            except Exception as e:
                st.error(f"Error procesando comentarios: {e}")
                return False
        return True

    # --- CALLBACKS DE ESTADO ---
    def _cb_actualizar_texto_lista(self, idx, widget_key):
        nuevo_texto = st.session_state[widget_key]
        st.session_state[self.json_key][self.seccion_json][idx]['content'] = nuevo_texto

    def _cb_eliminar_item(self, idx):
        st.session_state[self.json_key][self.seccion_json].pop(idx)

    def _cb_agregar_item(self):
        nuevo_item = {
            "title": f"Nueva {self.seccion_json}",
            "content": "",
            "priority": self.seccion_json,
            "references": []
        }
        st.session_state[self.json_key][self.seccion_json].append(nuevo_item)

    def _cb_actualizar_texto_plano(self, widget_key):
        st.session_state[self.json_key][self.seccion_json] = st.session_state[widget_key]

    # --- RENDERIZADORES ESPECÍFICOS ---
    def _renderizar_lista(self, contenido):
        for idx, item in enumerate(contenido):
            with st.container():
                titulo_original = item.get('title', f'Item {idx + 1}')
                st.caption(f"📝 {titulo_original}")
                
                content_key = f"{self.widget_prefix}_content_{idx}"
                
                st.text_area(
                    label=f"Contenido {idx}",
                    value=item.get('content', ''),
                    height=150,
                    key=content_key,
                    label_visibility="collapsed",
                    on_change=self._cb_actualizar_texto_lista,
                    args=(idx, content_key)
                )
                
                if len(contenido) > 1:
                    btn_del_key = f"{self.widget_prefix}_del_{idx}"
                    st.button(
                        "🗑️ Eliminar", 
                        key=btn_del_key, 
                        use_container_width=True,
                        on_click=self._cb_eliminar_item,
                        args=(idx,)
                    )
            st.divider()
        
        st.button(
            f"➕ Agregar nueva {self.seccion_json}", 
            key=f"{self.widget_prefix}_add",
            on_click=self._cb_agregar_item
        )

    def _renderizar_texto(self, contenido):
        texto_key = f"{self.widget_prefix}_text"
        st.text_area(
            label="Edición de texto",
            value=contenido,
            height=500,
            key=texto_key,
            label_visibility="collapsed",
            on_change=self._cb_actualizar_texto_plano,
            args=(texto_key,)
        )

    # --- MÉTODO PRINCIPAL ---
    def render(self):
        st.subheader(self.titulo_ui)

        if not self._cargar_datos():
            return None 
        
        data_dict = st.session_state[self.json_key]
        contenido_actual = data_dict.get(self.seccion_json, None)

        if contenido_actual is None:
            st.warning(f"No se encontró la sección '{self.seccion_json}' en el reporte.")
            return None

        if isinstance(contenido_actual, list):
            self._renderizar_lista(contenido_actual)
        elif isinstance(contenido_actual, str):
            self._renderizar_texto(contenido_actual)
        else:
            st.warning(f"Tipo de contenido no soportado para edición: {type(contenido_actual)}")