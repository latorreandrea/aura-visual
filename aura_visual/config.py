import os


def _env_int(name, default):
    """Read an integer environment variable, falling back to *default*."""
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


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
    # Static assets
    # -------------------------------------------------------------------------
    # Bump this value per deployment to force browser refresh of CSS/JS files.
    ASSET_VERSION = os.environ.get('ASSET_VERSION', '1')

    # -------------------------------------------------------------------------
    # CSRF Protection
    # -------------------------------------------------------------------------
    WTF_CSRF_ENABLED = True
    # Token lifetime in seconds. Overridable for long forms or slow connections.
    WTF_CSRF_TIME_LIMIT = _env_int('WTF_CSRF_TIME_LIMIT', 3600)

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
    # Google reCAPTCHA v2 (standard, free tier)
    # -------------------------------------------------------------------------
    RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY', '')
    RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY', '')

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

    #: Environment variables that must be present for a production deploy.
    REQUIRED_ENV_VARS = (
        'FLASK_SECRET_KEY',
        'RECAPTCHA_SITE_KEY',
        'RECAPTCHA_SECRET_KEY',
    )

    @classmethod
    def validate(cls):
        """Raise an error at startup if required production settings are missing."""
        # Only the variable names are reported: values are never logged.
        missing = [name for name in cls.REQUIRED_ENV_VARS if not os.environ.get(name)]
        if missing:
            raise RuntimeError(
                "Missing required environment variables: "
                + ", ".join(missing)
                + ". The contact form cannot be protected without them."
            )


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}