from flask import Blueprint

# Initialize the blueprint
merchant_bp = Blueprint('merchant', __name__, template_folder='templates')

# Import routes after initializing the blueprint
from . import routes
