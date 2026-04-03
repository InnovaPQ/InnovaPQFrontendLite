import json
import boto3
import streamlit as st
from botocore.exceptions import ClientError
import pandas as pd
from io import BytesIO, StringIO  # <-- Añadido StringIO aquí
from PIL import Image
import openpyxl


class Data:
    def __init__(self, folder="NA"):
        self.accessKeyID = st.secrets["aws"]["aws_access_key_id"]
        self.SecretAccessKey = st.secrets["aws"]["aws_secret_access_key"]
        self.Region = st.secrets["aws"]["region_name"]
        self.bucket = st.secrets["aws"]["bucket_name"]
        self.folder = folder
        
        self.client_s3 = boto3.client(
            's3',
            aws_access_key_id=self.accessKeyID,
            aws_secret_access_key=self.SecretAccessKey,
            region_name=self.Region
        )
        self.client_sqs = boto3.client(
            'sqs',
            aws_access_key_id=self.accessKeyID,
            aws_secret_access_key=self.SecretAccessKey,
            region_name=self.Region
        )

    def LeerDatos(self):
        data = json.load(open('ArchivosJson/DB_OrigenCodigoRed.json', 'r', encoding='utf-8'))
        return data
    
    def GuardarDatos(self, json_completo, ruta_s3):
        """
        Guarda el JSON completo de comentarios en S3.
        """
        try:
            json_bytes = json.dumps(json_completo, indent=4, ensure_ascii=False).encode('utf-8')
            
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
        Devuelve: El JSON con las rutas absolutas validadas en S3.
        """
        s3 = self.client_s3
        if not s3: return {}

        bucket_name = self.bucket
        
        json_template = self.LeerDatos()

        if not self.folder.endswith('/'): 
            self.folder += '/'

        print(f"📡 Escaneando S3 en: {self.folder}...")

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

        def actualizar_nodo(nodo):
            for clave, valor in nodo.items():
                if isinstance(valor, dict):
                    actualizar_nodo(valor)
                elif isinstance(valor, str):
                    ruta_relativa = valor.lstrip('/')
                    ruta_completa = f"{self.folder}{ruta_relativa}"

                    if ruta_completa in archivos_validos:
                        nodo[clave] = ruta_completa
                    else:
                        nodo[clave] = None
        
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

    def objeto_existe_s3(self, key: str) -> bool:
        if not key: return False
        try:
            self.client_s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code", "")
            if code in ("404", "NoSuchKey", "NotFound"):
                return False
            if code == "403":
                print(f"objeto_existe_s3: 403 en {key} (¿permisos?)")
            return False
        except Exception as e:
            print(f"objeto_existe_s3: {e}")
            return False

    def enviar_mensaje_sqs(self, queue_url, mensaje):
        try:
            body_preview = json.dumps(mensaje, ensure_ascii=False)
            print(
                f"[SQS] send_message queue={queue_url!r} "
                f"bytes={len(body_preview)} report_id={mensaje.get('report_id')!r}"
            )
            response = self.client_sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=body_preview
            )
            mid = response.get("MessageId", "")
            print(f"[SQS] OK MessageId={mid}")
            return response
        except Exception as e:
            print(f"Error enviando mensaje a SQS: {e}")
            raise e
        
    # =========================================================================
    # NUEVO MÉTODO PARA GUARDAR DATOS EDITADOS
    # =========================================================================
    def actualizar_archivo_s3(self, rutaDatos, df):
        """
        Recibe un DataFrame modificado desde Streamlit y lo sobreescribe en S3.
        Soporta archivos Excel (.xlsx) y CSV automáticamente.
        """
        try:
            # 1. Aseguramos el nombre del bucket y la llave
            if str(rutaDatos).startswith("s3://"):
                partes = rutaDatos.replace("s3://", "").split("/", 1)
                bucket_name = partes[0]
                key_name = partes[1]
            else:
                bucket_name = self.bucket # Usa el bucket de tus st.secrets
                key_name = rutaDatos

            # 2. Convertir DataFrame a bytes (Excel o CSV dependiendo de la ruta)
            if key_name.endswith(('.xlsx', '.xls')):
                buffer = BytesIO()
                # Usamos openpyxl para escribir el Excel en memoria
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                
                body_content = buffer.getvalue()
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            else:
                # Fallback a CSV por siaca
                buffer = StringIO()
                df.to_csv(buffer, index=False)
                body_content = buffer.getvalue()
                content_type = 'text/csv'

            # 3. Subir a S3
            self.client_s3.put_object(
                Bucket=bucket_name,
                Key=key_name,
                Body=body_content,
                ContentType=content_type
            )
            
            print(f"✅ Archivo guardado exitosamente en: s3://{bucket_name}/{key_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error crítico al intentar guardar en S3: {e}")
            return False