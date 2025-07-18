from google.cloud import secretmanager
from flask import current_app
import os

def get_secret(secret_name, project_id=None):
    """
    Retrieve a secret from Google Cloud Secret Manager
    """
    try:
        project_id = 'auravisual'
            
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        
        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode("UTF-8")
        
        current_app.logger.info(f"Successfully retrieved secret: {secret_name}")
        return secret_value
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving secret {secret_name}: {str(e)}")
        return None