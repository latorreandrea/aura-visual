import json
import time
import urllib.error
import urllib.parse
import urllib.request

from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory
from ..forms import ContactForm
from ..repositories.contact_repository import ContactRepository  
from ..utils.email_service import send_contact_notification
from .. import limiter

main = Blueprint('main', __name__)

RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'
RECAPTCHA_TIMEOUT_SECONDS = 5
RECAPTCHA_MAX_ATTEMPTS = 2


class RecaptchaError(ValueError):
    """A reCAPTCHA token was rejected or could not be verified.

    ``code`` is a stable machine readable identifier consumed by the browser,
    so the client can tell "solve the challenge again" apart from "Google is
    unreachable" without parsing human readable text.
    """

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def _siteverify(payload):
    """POST the token to Google and return ``(result, latency_ms)``.

    Retries once on transport errors: Google being slow or briefly unreachable
    is not the visitor's fault, so a single retry is attempted before giving up.
    """
    body = urllib.parse.urlencode(payload).encode('utf-8')
    last_error = None

    for attempt in range(1, RECAPTCHA_MAX_ATTEMPTS + 1):
        request_obj = urllib.request.Request(
            RECAPTCHA_VERIFY_URL,
            data=body,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            method='POST',
        )
        started = time.monotonic()
        try:
            with urllib.request.urlopen(request_obj, timeout=RECAPTCHA_TIMEOUT_SECONDS) as response:
                raw = response.read().decode('utf-8')
            # json.JSONDecodeError is a ValueError subclass, handled below.
            return json.loads(raw), (time.monotonic() - started) * 1000.0
        except (urllib.error.URLError, OSError, ValueError) as exc:
            last_error = exc
            current_app.logger.warning(
                'reCAPTCHA siteverify attempt %s/%s failed: %s',
                attempt, RECAPTCHA_MAX_ATTEMPTS, exc,
            )

    raise RecaptchaError(
        'recaptcha_unavailable',
        'Unable to verify reCAPTCHA. Please try again in a moment.',
    ) from last_error


def validate_recaptcha():
    """Verify the submitted reCAPTCHA v2 token with Google's siteverify API."""
    secret_key = current_app.config.get('RECAPTCHA_SECRET_KEY')
    site_key = current_app.config.get('RECAPTCHA_SITE_KEY')
    token = request.form.get('g-recaptcha-response', '').strip()

    if not secret_key:
        if not site_key:
            # reCAPTCHA is not configured at all (local development).
            current_app.logger.warning('reCAPTCHA keys are not configured; skipping verification.')
            return True
        current_app.logger.error('RECAPTCHA_SECRET_KEY is missing but a site key is configured.')
        raise RecaptchaError(
            'recaptcha_unavailable',
            'Verification is temporarily unavailable. Please try again later.',
        )

    if not token:
        current_app.logger.warning(
            'reCAPTCHA token missing (host=%s, path=%s)', request.host, request.path,
        )
        raise RecaptchaError(
            'recaptcha_missing_token',
            'Please complete the reCAPTCHA challenge.',
        )

    payload = {
        'secret': secret_key,
        'response': token,
    }
    if request.remote_addr:
        # Helps Google's risk analysis; harmless when absent.
        payload['remoteip'] = request.remote_addr

    result, latency_ms = _siteverify(payload)

    error_codes = result.get('error-codes') or []

    if not result.get('success'):
        # Never log the token or the secret: only shape and metadata.
        current_app.logger.warning(
            'reCAPTCHA rejected token: codes=%s hostname=%s request_host=%s '
            'token_len=%s latency_ms=%.1f',
            ','.join(error_codes) or 'none',
            result.get('hostname') or '-',
            request.host,
            len(token),
            latency_ms,
        )
        raise RecaptchaError(
            'recaptcha_failed:' + (','.join(error_codes) if error_codes else 'unknown'),
            'reCAPTCHA verification failed. Please solve the challenge again.',
        )

    current_app.logger.info(
        'reCAPTCHA accepted token: hostname=%s request_host=%s token_len=%s latency_ms=%.1f',
        result.get('hostname') or '-', request.host, len(token), latency_ms,
    )
    return True


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/submit_contact', methods=['POST'])
@limiter.limit('5 per hour')
def submit_contact():
    """
        Route to handle contact form submission.
        - Validates the form data
        - Saves the data to Firestore
        - Returns a JSON response
    """
    # Create the form instance and validate it
    form = ContactForm()
    
    if not form.validate_on_submit():
        # If the form is not valid, return the errors
        errors = {}
        for field, error_messages in form.errors.items():
            errors[field] = error_messages[0]  # Take only the first error for each field
        return jsonify({
            'success': False,
            'errors': errors,
            'message': 'Please correct the errors in the form'
        }), 400

    try:
        validate_recaptcha()
    except RecaptchaError as e:
        # ``code`` lets contact.js decide between "reset the widget" and
        # "retry later" instead of showing a generic failure.
        return jsonify({
            'success': False,
            'code': e.code,
            'message': str(e)
        }), 400
    
    try:
        # Obtain the form data and add the IP address
        form_data = form.data
        form_data['ip_address'] = request.remote_addr

        # Remove the csrf_token field before saving
        if 'csrf_token' in form_data:
            del form_data['csrf_token']

        # Save the data to Firestore
        repository = ContactRepository()
        doc_id = repository.save_contact(form_data)

        # Send a notification email
        try:
            email_sent = send_contact_notification(form_data)
        except Exception as e:
            current_app.logger.error(f"Error sending email: {str(e)}")
            email_sent = False

        # Success Log
        current_app.logger.info(f"Contact form submitted successfully. Doc ID: {doc_id}")
        
        return jsonify({
            'success': True,
            'message': 'Your message has been sent. Thank you!',
            'doc_id': doc_id
        })
        
    except ValueError as e:
        # Validation errors
        current_app.logger.warning(f"Contact form validation error: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
        
    except Exception as e:
        # Other errors
        current_app.logger.error(f"Error saving contact form: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while processing your request. Please try again later.'
        }), 500


@main.route('/sitemap.xml')
def sitemap():
    return send_from_directory(current_app.static_folder, 'sitemap.xml', mimetype='application/xml')


@main.route('/robots.txt')
def robots():
    return send_from_directory(current_app.static_folder, 'robots.txt', mimetype='text/plain')


@main.after_app_request
def apply_cache_headers(response):
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=86400'
    elif request.path in ['/robots.txt', '/sitemap.xml']:
        response.headers['Cache-Control'] = 'public, max-age=3600'
    return response