from flask import Flask
from .config import config

def create_app(config_name='default'):
    """Create an instance of the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # register blueprints
    from .routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Add other extensions here (Flask-SQLAlchemy, Flask-Login, etc.)
    
    return app