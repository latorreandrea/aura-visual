from flask import Flask, jsonify, request
from flask_wtf.csrf import CSRFProtect, CSRFError, generate_csrf
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from .config import config

# Import CSRF protection
# This is used to protect against CSRF attacks in Flask applications.
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)

def create_app(config_name='default'):
    """Create an instance of the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Fail fast on a broken production deploy: a missing secret or reCAPTCHA
    # key would otherwise leave the contact form silently unusable.
    validator = getattr(config[config_name], 'validate', None)
    if callable(validator):
        validator()

    # Cloud Run terminates TLS and forwards the real client address in
    # X-Forwarded-For. Without ProxyFix request.remote_addr is the shared
    # Google front end address (169.254.x.x) for every visitor, which breaks
    # per-client rate limiting and stores a useless ip_address in Firestore.
    # One trusted proxy hop is expected; revisit x_for if another proxy is
    # ever added in front of the service.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # Initialize CSRF protection    
    csrf.init_app(app)
    limiter.init_app(app)

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        """Answer CSRF failures with JSON the AJAX client can understand.

        The default HTML error page used to break ``response.json()`` in
        contact.js, so an expired token surfaced as a generic "Network error".
        """
        app.logger.warning(
            'CSRF validation failed: %s (host=%s, path=%s)',
            error.description, request.host, request.path,
        )
        payload = {
            'success': False,
            'code': 'csrf',
            'message': 'Your session expired. Please try again.',
        }
        try:
            # Hand out a replacement token so the client can retry silently
            # instead of losing everything the visitor already typed.
            payload['csrf_token'] = generate_csrf()
        except Exception as exc:  # pragma: no cover - defensive
            app.logger.warning('Could not issue a replacement CSRF token: %s', exc)
        return jsonify(payload), 400

    @app.errorhandler(429)
    def handle_rate_limit(error):
        """Return JSON for rate limited requests instead of an HTML page."""
        app.logger.warning(
            'Rate limit exceeded (host=%s, path=%s)', request.host, request.path,
        )
        return jsonify({
            'success': False,
            'code': 'rate_limited',
            'message': 'Too many messages from this connection. Please try again later.',
        }), 429
    
    # register blueprints
    from .routes.main import main as main_blueprint
    from .routes.your_card import your_card as your_card_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(your_card_blueprint)
    
    return app

