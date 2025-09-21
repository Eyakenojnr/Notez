import os
import logging
from config import Config
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from logging.handlers import RotatingFileHandler


# Find absolute path of the root of the backend directory
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# Load the .env file from that directory
load_dotenv(os.path.join(basedir, '.env'))

# Extension Initialization (Decoupled)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
cors = CORS()
jwt = JWTManager()

# App Factory Function
def create_app(config_class=Config):
    """Creates and configures an instance of the Flask application.

    Args:
        config_class (class, optional): Configuration class. Defaults to Config.

    Returns:
        object: Fully configured Flask app instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)  # Read & apply configs from config file

    # Connect extensions to the app using .init_app() to bind each extension to the app instance
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})  # scope CORS to API routes
    jwt.init_app(app)

    # Register Blueprints (connection of routes.py file)
    from app.api import bp as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    # Logging errors to file
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/notez.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Notez API startup')

    return app

from app import models
