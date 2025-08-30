from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)

# Read and apply configurations from the config file
app.config.from_object(Config)

# Flask-SQLAlchemy and Flask-Migrate initialization
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
