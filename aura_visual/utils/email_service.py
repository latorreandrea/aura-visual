import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def send_contact_notification(form_data):
    """
        sends a notification email when a user submits the contact form.
        Uses direct SMTP connection.
    """
    try:
        # Get email configuration
        smtp_server = current_app.config.get('MAIL_SERVER', 'smtp.zoho.eu')
        smtp_port = current_app.config.get('MAIL_PORT', 587)
        use_tls = current_app.config.get('MAIL_USE_TLS', True)
        username = current_app.config.get('MAIL_USERNAME')
        password = current_app.config.get('MAIL_PASSWORD')
        
        # Debug per vedere esattamente quali valori sono disponibili
        current_app.logger.info(f"SMTP Config: SERVER={smtp_server}, PORT={smtp_port}, TLS={use_tls}")
        current_app.logger.info(f"Username type: {type(username)}, length: {len(username) if username else 0}")
        current_app.logger.info(f"Password type: {type(password)}, length: {len(password) if password else 0}")
        
        # Verifica che username e password non siano None
        if not username or not password:
            current_app.logger.error("Username o password mancanti nelle configurazioni email")
            return False
        
        current_app.logger.info(f"Attempting to send email using {username} via direct SMTP")
        
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

            Message: {form_data.get('message')}
        """
        msg.attach(MIMEText(body, 'plain'))
        
        current_app.logger.info("Connecting to SMTP server...")
        
        # Connect to server and send
        if use_tls:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            
        current_app.logger.info("Attempting SMTP login...")
        server.login(username, password)
        
        current_app.logger.info("Sending email...")
        server.send_message(msg)
        server.quit()
        
        current_app.logger.info("Email notification sent successfully via direct SMTP")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Error sending email via direct SMTP: {str(e)}")
        return False