"""Web forms."""
import re
import sqlalchemy as sa
from app import db
from app.models import User, GenderEnum
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo


class LoginForm(FlaskForm):
    """Login form
    """

    username = StringField('Username', validators=[DataRequired('Enter a valid username')])
    password = PasswordField('Password', validators=[DataRequired('Please enter a password')])
    remember_me = BooleanField('Remember Me')
    submit_login = SubmitField('Sign In')


class SignupForm(FlaskForm):
    """User registration form.
    """

    first_name = StringField('Firstname', validators=[DataRequired('Must provide first name.')])
    last_name = StringField('Lastname')
    username = StringField('Username', validators=[DataRequired()]) # validation for blank, too short, too long inputs
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    password2 = StringField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    gender = RadioField(
        'Gender',
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other / Prefer not to say')],
        validators=[DataRequired()]
    )
    submit_signup = SubmitField('Create Account')

    def validate_username(self, username):
        """Custom validator for the username field.
        """
        # Check for existing user (uniqueness)
        if db.session.scalar(sa.select(User).where(User.username == username.data)):
            raise ValidationError('Username is already in use. Please choose a different one.')
        
        # Check length
        if len(username.data) < 4 or len(username.data) > 10:
            raise ValidationError('Username must be between 4 and 10 characters long.')
        
        RESERVED_USERNAMES =['admin', 'root', 'support', 'help', 'api', 'auth', 'login', 'register']
        if username.data.lower() in RESERVED_USERNAMES:
            raise ValidationError("This username is reserved, choose another.")
        
        # Checking format using regular expression
        # ^[a-zA-Z]     - Must start with a letter (upper or lowercase)
        # [a-zA-Z0-9]*  - Can be followed by any number of letters or numbers
        # $             - Must end here (no trailing symbols)
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', username.data):
            raise ValidationError("Username must start with a letter and contain only letters and numbers.")
        
    def validate_email(self, email):
        """Custom validator for the email field."""
        if db.session.scalar(sa.select(User).where(User.email == email.data)):
            raise ValidationError('Email address already in use.')
        
    def validate_password(self, password):
        """Validates password strength:
            - At least 6 characters
            - At least one uppercase letter
            - At least one lowercase letter
            - At least one number
            - At least one special character
        """
        p = password.data
        if len(p) < 6:
            raise ValidationError("Password must be at least 6 characters long.")
        if not re.search(r'[A-Z]', p):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', p):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'[0-9]', p):
            raise ValidationError("Password must contain at least one number.")
        if not re.search(r'[\W_]', p):  # \W => non-alphanumeric
            raise ValidationError("Password must contain at least one special character.")
