import base64
import json
import os
from typing import Dict, Any
import time
import logging
import requests
from google.auth.transport.requests import Request
from google.oauth2 import id_token
import google.cloud.logging
import google.auth


# Configurar logging
client = google.cloud.logging.Client()
client.setup_logging()
logging.basicConfig(level=logging.INFO)

# Configuración
PROJECT_ID = os.environ.get("PROJECT_ID")
REGION = os.environ.get("REGION", "us-central1")
JOB_NAME = os.environ.get("JOB_NAME", "bot-processor")
AUDIENCE = f"https://{REGION}-run.googleapis.com"
RUN_JOB_URL = f"{AUDIENCE}/apis/run.googleapis.com/v1/namespaces/{PROJECT_ID}/jobs/{JOB_NAME}:run"

def get_auth_token(audience=None):
    """
    Obtiene un token de autenticación para acceder a las APIs de Google Cloud.

    Args:
        audience: URL base para la autenticación (por defecto usa el AUDIENCE global)

    Returns:
        Token de autenticación
    """
    try:
        # Método 1: Usando google.auth.default() - método recomendado para entornos GCP
        credentials, project_id = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_req = Request()
        credentials.refresh(auth_req)
        return credentials.token
    except Exception as e:
        logging.warning(f"Error al obtener token con google.auth.default: {e}")
        try:
            # Método 2: Usando id_token.fetch_id_token() - alternativo
            target_audience = audience or AUDIENCE
            token = id_token.fetch_id_token(Request(), target_audience)
            return token
        except Exception as e2:
            logging.error(f"Error al obtener token con id_token.fetch_id_token: {e2}")
            raise Exception(f"No se pudo obtener token de autenticación: {e2}")


# Obtener token de autenticación
token = get_auth_token()

# Headers de autenticación y contenido
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
# Activar el Cloud Run Job
response = requests.post(
    RUN_JOB_URL,
    headers=headers,
    json={}  # Payload vacío
)
