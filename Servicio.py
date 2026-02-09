import json
import boto3
import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image
import openpyxl


class Data:
    def __init__(self,folder="NA"):
        self.accessKeyID=st.secrets["aws"]["aws_access_key_id"]
        self.SecretAccessKey=st.secrets["aws"]["aws_secret_access_key"]
        self.Region=st.secrets["aws"]["region_name"]
        self.bucket=st.secrets["aws"]["bucket_name"]
        self.folder=folder
        self.client_s3=boto3.client(
                                    's3',
                                    aws_access_key_id=self.accessKeyID,
                                    aws_secret_access_key=self.SecretAccessKey,
                                    region_name=self.Region
                                )
        self.client_sqs=boto3.client(
                                    'sqs',
                                    aws_access_key_id=self.accessKeyID,
                                    aws_secret_access_key=self.SecretAccessKey,
                                    region_name=self.Region
                                )
        

    def LeerDatos(self):
        data=json.load(open('ArchivosJson/DB_OrigenCodigoRed.json', 'r', encoding='utf-8'))
        return data
    
    def GuardarDatos(self, json_completo, ruta_s3):
        """
        Guarda el JSON completo de comentarios en S3.
        
        Args:
            json_completo (dict): El JSON completo con todas las secciones
            ruta_s3 (str): La ruta completa en S3 donde se guardará el JSON
        """
        try:
            # Convertir el JSON a bytes
            json_bytes = json.dumps(json_completo, indent=4, ensure_ascii=False).encode('utf-8')
            
            # Subir a S3
            self.client_s3.put_object(
                Bucket=self.bucket,
                Key=ruta_s3,
                Body=json_bytes,
                ContentType='application/json'
            )
        except Exception as e:
            print(f"Error guardando datos en S3: {e}")
            raise e

    def obtener_rutas_actualizadas(self):
        """
        Recibe: 'Clientes/CocaCola/2024'
        Devuelve: El JSON con las rutas absolutas validadas en S3.
        """
        s3 = self.client_s3
        if not s3: return {}

        bucket_name = self.bucket
        
        # 1. Cargar el mapa base (Tu JSON local)
        json_template = self.LeerDatos()

        # 2. Normalizar la carpeta raíz (asegurar que termine en /)
        if not self.folder.endswith('/'): 
            self.folder += '/'

        print(f"📡 Escaneando S3 en: {self.folder}...")

        # 3. Obtener Inventario Real (Set para búsqueda instantánea)
        archivos_validos = set()
        paginator = s3.get_paginator('list_objects_v2')
        
        try:
            pages = paginator.paginate(Bucket=bucket_name, Prefix=self.folder)
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        archivos_validos.add(obj['Key'])
        except Exception as e:
            st.error(f"Error leyendo el bucket: {e}")
            return json_template

        # 4. Recorrer el JSON y rellenar las rutas (Recursivo)
        def actualizar_nodo(nodo):
            for clave, valor in nodo.items():
                if isinstance(valor, dict):
                    # Si es carpeta lógica (ej: "Contexto"), entramos
                    actualizar_nodo(valor)
                elif isinstance(valor, str):
                    # --- AQUÍ OCURRE LA MAGIA ---
                    # Limpiamos slashes iniciales para evitar dobles //
                    ruta_relativa = valor.lstrip('/')
                    
                    # Construimos la ruta absoluta
                    # Ej: "CarpetaRaiz/" + "Armonicos/espectros/foto.png"
                    ruta_completa = f"{self.folder}{ruta_relativa}"

                    # Verificamos si existe en la lista que bajamos de S3
                    if ruta_completa in archivos_validos:
                        nodo[clave] = ruta_completa
                    else:
                        # Si no existe, lo marcamos explícitamente como None
                        # print(f"❌ No encontrado: {ruta_completa}")
                        nodo[clave] = None
        
        # Trabajamos sobre una copia para no alterar el original en memoria
        json_final = json_template.copy()
        actualizar_nodo(json_final)
        
        return json_final
    
    def descargar_archivo_s3(self, s3_key):
        if not s3_key: return None
        try:
            obj = self.client_s3.get_object(Bucket=self.bucket, Key=s3_key)
            contenido = obj['Body'].read()

            if s3_key.endswith(('.xlsx', '.xls')):
                return pd.read_excel(BytesIO(contenido))
            elif s3_key.endswith(('.png', '.jpg', '.jpeg')):
                return Image.open(BytesIO(contenido))
            else:
                return contenido
        except Exception as e:
            print(f"Error descargando: {e}")
            return None

    def enviar_mensaje_sqs(self, queue_url, mensaje):
        """
        Envía un mensaje JSON a una cola SQS.
        mensaje: dict que se serializará a JSON string
        """
        try:
            response = self.client_sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(mensaje)
            )
            return response
        except Exception as e:
            print(f"Error enviando mensaje a SQS: {e}")
            raise e

    
        
        
