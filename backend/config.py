"""Configuration file."""
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    #SQLALCHEMY_ECHO = True
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    WTF_CSRF_ENABLED = False
