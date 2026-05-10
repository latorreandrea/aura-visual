import os

class Config:
    # -------------------------------------------------------------------------
    # Security
    # -------------------------------------------------------------------------
    # FLASK_SECRET_KEY must always be set via environment variable in production.
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-key-for-development'

    # -------------------------------------------------------------------------
    # Google Cloud
    # -------------------------------------------------------------------------
    GOOGLE_CLOUD_PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT')

    # -------------------------------------------------------------------------
    # CSRF Protection
    # -------------------------------------------------------------------------
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # Token expires after 1 hour

    # -------------------------------------------------------------------------
    # Email (SMTP via Zoho)
    # -------------------------------------------------------------------------
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.zoho.eu')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'info@auravisual.dk')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'info@auravisual.dk')

    # -------------------------------------------------------------------------
    # Your Card — product page defaults (overridable via env vars)
    # -------------------------------------------------------------------------
    YOUR_CARD_PRODUCT_NAME = os.environ.get('YOUR_CARD_PRODUCT_NAME', 'Your Card')
    YOUR_CARD_PRODUCT_DESCRIPTION = os.environ.get(
        'YOUR_CARD_PRODUCT_DESCRIPTION',
        'A simple and focused product offer designed to present value clearly.'
    )
    YOUR_CARD_PRODUCT_PRICE = os.environ.get('YOUR_CARD_PRODUCT_PRICE', 'Contact us')
    YOUR_CARD_PRODUCT_CURRENCY = os.environ.get('YOUR_CARD_PRODUCT_CURRENCY', 'DKK')

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    # In local development, the Google SDK picks up GOOGLE_APPLICATION_CREDENTIALS
    # automatically from the OS environment (set in .env). No extra Flask config needed.


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

    @classmethod
    def validate(cls):
        """Raise an error at startup if required production secrets are missing."""
        if not os.environ.get('FLASK_SECRET_KEY'):
            raise RuntimeError(
                "FLASK_SECRET_KEY environment variable is not set. "
                "This is required in production."
            )


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}