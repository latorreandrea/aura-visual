import datetime
from ..services.db import get_firestore_client

class ContactRepository:
    """Repository for managing contact operations in Firestore."""
    
    def __init__(self):
        self.db = get_firestore_client()
        self.collection = self.db.collection('contact_requests')
    
    def save_contact(self, form_data):
        """
        Save contact form data to Firestore.
        
        Args:
            form_data: dictionary with form data

        Returns:
            str: ID of the created document
        """
        data = {
            'name': form_data.get('name', ''),
            'email': form_data.get('email', ''),
            'phone': form_data.get('phone', ''),
            'project_name': form_data.get('project_name', ''),
            'message': form_data.get('message', ''),
            'created_at': datetime.datetime.now(),
            'ip_address': form_data.get('ip_address', '')
        }

        # Data validation
        if not data['name'] or not data['email'] or not data['project_name']:
            raise ValueError("Name, email, and project name are required.")

        # Add the document to the database
        doc_ref = self.collection.add(data)
        return doc_ref[1].id  # Return the ID of the created document