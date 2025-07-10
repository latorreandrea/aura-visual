from flask_mail import Message
from flask import current_app
from aura_visual import mail

def send_contact_notification(form_data):
    """
        sends a notification email when a user submits the contact form.
    """
    try:
        subject = f"New Contact: {form_data.get('name')} - {form_data.get('project_name')}"
        
        body = f"""
You have received a new contact form submission:

Name: {form_data.get('name')}
Email: {form_data.get('email')}
Phone: {form_data.get('phone', 'Not provided')}
Project: {form_data.get('project_name')}

Message:
{form_data.get('message')}
        """        
        msg = Message(
            subject=subject,
            recipients=['info@auravisual.dk'],
            body=body,
            sender='info@auravisual.dk'
        )
        
        # Set the reply-to address if provided
        if form_data.get('email'):
            msg.reply_to = form_data.get('email')
            
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending email: {str(e)}")
        return False