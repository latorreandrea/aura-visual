import json
import urllib.request
import urllib.parse

from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory
from ..forms import ContactForm
from ..repositories.contact_repository import ContactRepository  
from ..utils.email_service import send_contact_notification
from .. import limiter

main = Blueprint('main', __name__)


def validate_recaptcha():
    """Verify Google reCAPTCHA v2 token using the free standard endpoint."""
    secret_key = current_app.config.get('RECAPTCHA_SECRET_KEY')
    token = request.form.get('g-recaptcha-response', '').strip()

    if not secret_key:
        current_app.logger.warning('reCAPTCHA secret key is missing; skipping verification.')
        return True

    if not token:
        raise ValueError('Please complete the reCAPTCHA challenge.')

    payload = urllib.parse.urlencode({
        'secret': secret_key,
        'response': token,
    }).encode('utf-8')

    request_obj = urllib.request.Request(
        'https://www.google.com/recaptcha/api/siteverify',
        data=payload,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        method='POST',
    )

    try:
        with urllib.request.urlopen(request_obj, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
    except Exception as exc:
        current_app.logger.error(f'reCAPTCHA verification error: {exc}')
        raise ValueError('Unable to verify reCAPTCHA. Please try again.')

    if not result.get('success'):
        current_app.logger.warning(f'reCAPTCHA failed: {result.get("error-codes")}')
        raise ValueError('Please complete the reCAPTCHA challenge correctly.')

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
    except ValueError as e:
        return jsonify({
            'success': False,
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