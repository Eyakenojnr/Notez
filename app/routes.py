from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, SignupForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app.models import User
from urllib.parse import urlsplit


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    """Landing page.
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    # Receive login credentials
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password!')
            # return redirect(url_for('index'))
            return render_template('index.html', title='Welcome Page', form=form)
        login_user(user, remember=form.remember_me.data)

        # Redirect  to \"next\" page
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)

    return render_template('index.html', title='Welcome Page', form=form)

@app.route('/logout')
def logout():
    """Logout view function.
    """
    logout_user()
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User signup view function"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = SignupForm()
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data, last_name=form.last_name.data,
                    username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f"Welcome {user.username}! Your account has been created successfully.")
        # Log the new user in automatically after signup
        #return redirect(url_for('index'))
        login_user(user)
        return redirect(url_for('home'))
    return render_template('signup.html', title='Signup', form=form)

@app.route('/home')
@login_required
def home():
    return render_template('home.html', title='Home Page')
