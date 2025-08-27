from app import app
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    """Welcome page.
    """
    #user = {'username': 'taddyP'}

    # Receive login credentials
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'Login requested for user {form.username.data}, remember_me={form.remember_me.data}')
        return redirect(url_for('home'))

    return render_template('index.html', title='Welcome Page', form=form)


@app.route('/home')
def home():
    return render_template('home.html')
