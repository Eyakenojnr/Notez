from flask import Flask
from config import Config


app = Flask(__name__)

# Read and apply configurations from the config file
app.config.from_object(Config)

from app import routes
