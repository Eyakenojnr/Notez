"""Blueprint for API routes.
"""
from flask import Blueprint


bp = Blueprint('api', __name__)

# Imported routes at the bottom to avoid circular dependencies
from app.api import routes#, errors
