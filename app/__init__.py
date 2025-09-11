from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


app = Flask(__name__)

# Read and apply configurations from the config file
app.config.from_object(Config)

# Flask-SQLAlchemy and Flask-Migrate initialization
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask-Login initialization
login = LoginManager(app)
login.login_view = 'index'  # Tell Flask-Login the view function that handles logins

from app import routes, models
