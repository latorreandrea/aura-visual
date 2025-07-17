import os
from dotenv import load_dotenv

# Load .env ONLY in development (non-Cloud Run) environments
is_cloud_run = os.environ.get('K_SERVICE') is not None
if not is_cloud_run and os.path.exists('.env'):
    load_dotenv()

class Config:
    # Base Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-development'
    GOOGLE_CLOUD_PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT')
    
    # CSRF Configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Email configuration for direct SMTP (used by smtplib)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.zoho.eu')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    # Default values for email credentials
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'info@auravisual.dk')  
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')  # Empty value as fallback
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'info@auravisual.dk')

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}