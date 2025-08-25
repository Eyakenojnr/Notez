from app import app


@app.route('/')
@app.route('/index')
def index():
    """Home page.
    """
    return "Welcome to my Notez taking app."
