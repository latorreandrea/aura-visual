from flask import Blueprint, render_template, request, jsonify, current_app
from ..forms import ContactForm
from ..repositories.contact_repository import ContactRepository  # Add this import

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/submit_contact', methods=['POST'])
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
        # Obtain the form data and add the IP address
        form_data = form.data
        form_data['ip_address'] = request.remote_addr

        # Remove the csrf_token field before saving
        if 'csrf_token' in form_data:
            del form_data['csrf_token']

        # Save the data to Firestore
        repository = ContactRepository()
        doc_id = repository.save_contact(form_data)
        
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