from flask import Flask
from flask_wtf.csrf import CSRFProtect
from .config import config
from flask_mail import Mail
import os

# Import CSRF protection
# This is used to protect against CSRF attacks in Flask applications.
csrf = CSRFProtect()
# Initialize Flask-Mail for sending emails
mail = Mail()

def create_app(config_name='default'):
    """Create an instance of the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # Initialize CSRF protection    
    csrf.init_app(app)
    # Initialize Flask-Mail
    mail.init_app(app)
    # register blueprints
    from .routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app

