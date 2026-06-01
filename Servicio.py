import json
import os

import boto3
import streamlit as st
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.config import Config
from botocore.exceptions import ClientError
from botocore.httpsession import URLLib3Session
import pandas as pd
from io import BytesIO, StringIO  # <-- Añadido StringIO aquí
from PIL import Image
import openpyxl


def _resolve_aws_secret(key: str) -> str:
    """Resuelve una clave AWS desde st.secrets."""
    try:
        val = st.secrets["aws"].get(key)
        if val is not None and str(val).strip():
            return str(val).strip()
    except Exception:
        pass
    return ""


class Data:
    def __init__(self, folder="NA"):
        # Configuración no sensible — siempre requerida en secrets.toml
        self.Region = st.secrets["aws"]["region_name"]
        self.bucket = st.secrets["aws"]["bucket_name"]
        self.folder = folder

        # Credenciales opcionales:
        #   - Local: se leen de secrets.toml si están presentes
        #   - EC2 con IAM Role: no se definen aquí; boto3 las obtiene
        #     automáticamente del Instance Metadata Service (IMDS)
        aws_key = st.secrets["aws"].get("aws_access_key_id")
        aws_secret = st.secrets["aws"].get("aws_secret_access_key")
        aws_token = st.secrets["aws"].get("aws_session_token")
        creds = {}
        if aws_key and aws_secret:
            creds = {
                "aws_access_key_id": aws_key,
                "aws_secret_access_key": aws_secret,
            }
            if aws_token:
                creds["aws_session_token"] = aws_token

        self._boto_creds = creds
        lambda_config = Config(
            connect_timeout=15,
            read_timeout=600,
            retries={"max_attempts": 2},
        )
        self.client_s3 = boto3.client("s3", region_name=self.Region, **creds)
        self.client_sqs = boto3.client("sqs", region_name=self.Region, **creds)
        self.client_lambda = boto3.client(
            "lambda", region_name=self.Region, config=lambda_config, **creds
        )

    def _frozen_credentials(self):
        session = boto3.Session(region_name=self.Region, **self._boto_creds)
        creds = session.get_credentials()
        if creds is None:
            raise RuntimeError(
                "No hay credenciales AWS (secrets o IAM role). "
                "Configure aws_access_key_id/aws_secret_access_key o un rol en EC2."
            )
        return creds.get_frozen_credentials()

    @staticmethod
    def _parse_column_check_response(raw: str) -> dict:
        parsed = json.loads(raw)
        if isinstance(parsed, dict) and "statusCode" in parsed:
            inner = parsed.get("body")
            if isinstance(inner, str):
                parsed = json.loads(inner)
            elif isinstance(inner, dict):
                parsed = inner
        return parsed

    def _check_columns_invoke(self, function_name: str, payload: dict) -> dict:
        """Invocación directa (lambda:InvokeFunction). Evita 403 de Function URL IAM."""
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        print(
            f"[column_check] invoke {function_name!r} report_id={payload.get('report_id')!r} "
            f"input={payload.get('input_key') or payload.get('input_keys')!r}"
        )
        try:
            response = self.client_lambda.invoke(
                FunctionName=function_name,
                InvocationType="RequestResponse",
                Payload=body,
            )
        except ClientError as e:
            raise RuntimeError(
                f"Column check invoke falló ({function_name}): {e}"
            ) from e

        raw = response["Payload"].read().decode("utf-8", errors="replace")
        print(f"[column_check] invoke done status={response.get('StatusCode')} bytes={len(raw)}")

        if response.get("FunctionError"):
            raise RuntimeError(f"Column check Lambda error: {raw[:800]}")

        try:
            return self._parse_column_check_response(raw)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"Respuesta Lambda no es JSON válido: {raw[:300]}"
            ) from e

    def _check_columns_function_url(self, function_url: str, payload: dict) -> dict:
        """POST firmado (SigV4) a Function URL — requiere lambda:InvokeFunctionUrl en IAM."""
        body_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        request = AWSRequest(
            method="POST",
            url=function_url,
            data=body_bytes,
            headers=headers,
        )
        SigV4Auth(self._frozen_credentials(), "lambda", self.Region).add_auth(request)
        prepared = request.prepare()

        http = URLLib3Session()
        try:
            response = http.send(prepared)
        except Exception as e:
            raise RuntimeError(f"Column check HTTP request failed: {e}") from e

        raw = (response.text or response.content.decode("utf-8", errors="replace"))
        if response.status_code >= 400:
            raise RuntimeError(
                f"Column check HTTP {response.status_code}: {raw[:500]}"
            )

        return self._parse_column_check_response(raw)

    def check_columns(self, payload: dict) -> dict:
        """
        Chequeo preventivo de columnas.

        Preferencia: aws.column_check_function_name + lambda:InvokeFunction
        (evita 403 si el usuario IAM no tiene lambda:InvokeFunctionUrl).
        Alternativa: column_check_function_url con SigV4.
        """
        function_name = (
            os.environ.get("COLUMN_CHECK_FUNCTION_NAME", "").strip()
            or _resolve_aws_secret("column_check_function_name")
        )
        if function_name:
            return self._check_columns_invoke(function_name, payload)

        function_url = (
            os.environ.get("COLUMN_CHECK_FUNCTION_URL", "").strip()
            or _resolve_aws_secret("column_check_function_url")
        )
        if not function_url:
            raise RuntimeError(
                "Configure aws.column_check_function_name (recomendado) o "
                "aws.column_check_function_url en secrets. "
                "Nombre: output CreateAssetsFunctionName del stack o "
                "`aws lambda list-functions --query \"Functions[?contains(FunctionName,"
                " 'CreateAssets')].FunctionName\"`."
            )
        return self._check_columns_function_url(function_url, payload)

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