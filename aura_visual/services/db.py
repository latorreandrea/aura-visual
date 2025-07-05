from google.cloud import firestore
from flask import current_app
import os

def get_firestore_client():
    """
        Returns an authenticated Firestore client 
        based on the environment.
    """
    project_id = current_app.config.get('GOOGLE_CLOUD_PROJECT')
    
    if project_id:
        return firestore.Client(project=project_id)
    else:
        return firestore.Client()