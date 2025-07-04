import os
# use dotenv to load environment variables from a .env file in local
from dotenv import load_dotenv


# Load .env only if we are not in production (Cloud Run)
is_cloud_run = os.environ.get('K_SERVICE') is not None
if not is_cloud_run and os.path.exists('.env'):
    load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-development'
    GOOGLE_CLOUD_PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT')
    # CSRF Configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    # use Google Cloud credentials in local development
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    # 'testing': TestingConfig,
    'default': DevelopmentConfig
}