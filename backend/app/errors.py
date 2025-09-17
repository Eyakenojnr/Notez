"""Custom error handlers.
"""
from flask import jsonify
from app import db
from app.api import bp as api_blueprint

# ------ API-Specific Error Handlers -------

@api_blueprint.app_errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not Found'}), 404

@api_blueprint.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Prevents broken database sessions after an error
    return jsonify({'error': 'Internal Server Error'}), 500

@api_blueprint.app_errorhandler(400)
def bad_request_error(error):
    message = error.description if hasattr(error, 'description') else 'Bad Request'
    return jsonify({'error': message}), 400
