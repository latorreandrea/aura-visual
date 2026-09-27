from google.cloud import firestore
from flask import current_app
import os

_firestore_clients = {}

def get_firestore_client():
    """
        Returns an authenticated Firestore client 
        based on the environment.
    """
    project_id = current_app.config.get('GOOGLE_CLOUD_PROJECT')
    
    client_key = project_id or '__default__'

    if client_key not in _firestore_clients:
        if project_id:
            _firestore_clients[client_key] = firestore.Client(project=project_id)
        else:
            _firestore_clients[client_key] = firestore.Client()

    return _firestore_clients[client_key]