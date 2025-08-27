"""Web forms"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    """Login form
    """

    username = StringField('Username', validators=[DataRequired('Enter a valid username')])
    password = PasswordField('Password', validators=[DataRequired('Please enter a password')])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
