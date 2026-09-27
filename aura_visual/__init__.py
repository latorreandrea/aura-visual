from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .config import config
import os

# Import CSRF protection
# This is used to protect against CSRF attacks in Flask applications.
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)

def create_app(config_name='default'):
    """Create an instance of the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # Initialize CSRF protection    
    csrf.init_app(app)
    limiter.init_app(app)
    
    # register blueprints
    from .routes.main import main as main_blueprint
    from .routes.your_card import your_card as your_card_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(your_card_blueprint)
    
    return app

