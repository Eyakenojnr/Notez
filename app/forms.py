"""Web forms"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
import sqlalchemy as sa
from app import db
from app.models import User


class LoginForm(FlaskForm):
    """Login form
    """

    username = StringField('Username', validators=[DataRequired('Enter a valid username')])
    password = PasswordField('Password', validators=[DataRequired('Please enter a password')])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class SignupForm(FlaskForm):
    """User registration form.
    """

    first_name = StringField('Firstname', validators=[DataRequired('Must provide first name.')])
    last_name = StringField('Lastname')
    username = StringField('Username', validators=[DataRequired()]) # validation for blank, too short, too long inputs
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    password2 = StringField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Custom validator to validate username input...
        """
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError('Use a different username, this is taken!')
        
    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')
