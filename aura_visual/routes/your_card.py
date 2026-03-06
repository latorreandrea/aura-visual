from flask import Blueprint, current_app, render_template


your_card = Blueprint('your_card', __name__, url_prefix='/your-card')


@your_card.route('/', methods=['GET'])
def index():
    """Render a product presentation page for Your Card."""
    product = {
        'name': current_app.config.get('YOUR_CARD_PRODUCT_NAME', 'Your Card'),
        'description': current_app.config.get(
            'YOUR_CARD_PRODUCT_DESCRIPTION',
            'A simple and focused product offer designed to present value clearly.'
        ),
        'price': current_app.config.get('YOUR_CARD_PRODUCT_PRICE', 'Contact us'),
        'currency': current_app.config.get('YOUR_CARD_PRODUCT_CURRENCY', 'DKK')
    }
    return render_template('your_card/index.html', product=product)
