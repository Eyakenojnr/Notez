from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, SignupForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app.models import User, GenderEnum
from urllib.parse import urlsplit


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    """Landing page.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    login_form = LoginForm()
    signup_form = SignupForm()

    # CASE 1: Login form is submitted
    if 'submit_login' in request.form and login_form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == login_form.username.data))
        if user is None or not user.check_password(login_form.password.data):
            flash("Invalid username or password!")
            # Re-render the page with an error so the form data is preserved
            return render_template('index.html', title="Welcome Page", login_form=login_form,
                                   signup_form=signup_form)
        login_user(user, remember=login_form.remember_me.data)

        # Redirect to \"next\" page
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('dashboard')
        return redirect(next_page)
    
    # CASE 2: Signup form is submitted
    if 'submit_signup' in request.form and signup_form.validate_on_submit():
        user = User(
            first_name=signup_form.first_name.data,
            last_name=signup_form.last_name.data,
            username=signup_form.username.data,
            email=signup_form.email.data,
            gender=GenderEnum(signup_form.gender.data)
        )
        user.set_password(signup_form.password.data)
        db.session.add(user)
        db.session.commit()

        # Automatically log the new user in and send them to the dashboard
        flash(f"Welcome {user.username}! Your account have been created successfully.")
        login_user(user)
        return redirect(url_for('dashboard'))

    return render_template('index.html', title='Welcome Page', login_form=login_form,
                           signup_form=signup_form)


@app.route('/logout')
def logout():
    """Logout view function.
    """
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashoard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')


@app.route('/user/<username>')
@login_required
def user(username):
    """User profile view function"""
    user = db.first_or_404(sa.select(User).where(User.username == username))
    return render_template('user.html', user=user)
