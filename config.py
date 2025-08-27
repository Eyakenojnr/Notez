"""Configuration file."""
import os


class Config:
    SECRET_KEY = os.environ.get('MY_KEY') or 'a-b-c-d'
