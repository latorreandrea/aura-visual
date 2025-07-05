from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, TelField
from wtforms.validators import DataRequired, Email, Length, ValidationError
import re

class ContactForm(FlaskForm):
    """
        Form for validating contact data.
    """
    
    name = StringField('Your Name', validators=[
        DataRequired(message="Please enter your name"),
        Length(min=2, max=50, message="Name must be between 2 and 50 characters")
    ])
    
    email = StringField('Your Email', validators=[
        DataRequired(message="Please enter your email"),
        Email(message="Please enter a valid email address")
    ])
    
    phone = TelField('Phone Number')
    
    project_name = StringField('Project Name', validators=[
        DataRequired(message="Please enter a project name"),
        Length(min=2, max=100, message="Project name must be between 2 and 100 characters")
    ])
    
    message = TextAreaField('Project Description', validators=[
        DataRequired(message="Please describe your project"),
        Length(min=20, max=2000, message="Description must be between 20 and 2000 characters")
    ])
    
    def validate_phone(self, field):
        """Custom validation for phone number."""
        if field.data:
            # Remove spaces, dashes, and parentheses
            phone = re.sub(r'[\s\-\(\)]', '', field.data)

            # Check if it's a valid number
            if not re.match(r'^\+?[0-9]{8,15}$', phone):
                raise ValidationError('Please enter a valid phone number')