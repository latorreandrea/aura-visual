import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def send_contact_notification(form_data):
    """
    sends a notification email when a user submits the contact form.
    Uses direct SMTP connection with secrets from Secret Manager.
    """
    try:
        # Detect environment
        is_cloud_run = os.environ.get('K_SERVICE') is not None
        
        if is_cloud_run:
            # In Cloud Run: use environment variables
            username = os.environ.get('MAIL_USERNAME')
            password = os.environ.get('MAIL_PASSWORD')
        else:
            # In local development: use config from .env
            username = current_app.config.get('MAIL_USERNAME')
            password = current_app.config.get('MAIL_PASSWORD')

        # Get email configuration from app config
        smtp_server = current_app.config.get('MAIL_SERVER', 'smtp.zoho.eu')
        smtp_port = current_app.config.get('MAIL_PORT', 587)
        use_tls = current_app.config.get('MAIL_USE_TLS', True)
        
        # Keep logs minimal and avoid leaking operational details/secrets.
        current_app.logger.info('Preparing contact notification email')
        
        # Validate credentials
        if not username or not password:
            current_app.logger.error('Email credentials are missing')
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = ', '.join(['latorre.andrea.93@gmail.com', 'rorro.arrieta.f@gmail.com'])
        msg['Subject'] = f"New Contact: {form_data.get('name')} - {form_data.get('project_name')}"
        
        # Set reply-to if available
        if form_data.get('email'):
            msg.add_header('Reply-To', form_data.get('email'))
        
        # Create email body

        body = f"""
You have received a new contact form submission:

Name: {form_data.get('name')}
Email: {form_data.get('email')}
Phone: {form_data.get('phone', 'Not provided')}
Project: {form_data.get('project_name')}
Company: {form_data.get('company', 'Not provided')}

Message: {form_data.get('message')}
        """
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to server and send
        if use_tls:
            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=10) as server:
                server.login(username, password)
                server.send_message(msg)
        
        current_app.logger.info('Contact notification email sent')
        return True
        
    except Exception as e:
        current_app.logger.error(f'Email send error: {str(e)}')
        return False