from app import db
from app.api import bp
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import sqlalchemy as sa
from app.models import User, GenderEnum


# ------ Authentication API Endpoints -------

@bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint.
    """
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'msg': 'Missing username, email, or password'}), 400
    
    # Check if username or email already exists
    if db.session.scalar(sa.select(User).where(User.username == data['username'])):
        return jsonify({'msg': 'Username already exists'}), 409  # 409 Conflict
    if db.session.scalar(sa.select(User).where(User.email == data['email'])):
        return jsonify({'msg': 'Email already exists'}), 409
    
    user = User(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=data.get('email'),
        gender=GenderEnum(data.get('gender')) if data.get('gender') else None
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'msg': 'User created successfully'}), 201  # 201 Created


@bp.route('/login', methods=['POST'])
def login():
    """User login endpoint. Returns an access token.
    """
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'msg': 'Missing username or password'}), 400
    
    user = db.session.scalar(sa.select(User).where(User.username == data['username']))

    if user is None or not user.check_password(data['password']):
        return jsonify({'msg': 'Bad username or password'}), 401  # 401 Unauthorized
    
    # Create the token. 'identity' can be anything unique to the user.
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token)


# ------ User Data API Endpoints -------

@bp.route('/profile')
@jwt_required()  # This decorator protects the routes
def my_profile():
    """Returns profile of the currently logged-in user.
    """
    current_user_id = get_jwt_identity()  # Get the user's ID from the token
    user = db.session.get(User, current_user_id)

    if user is None:
        return jsonify({'msg': 'User not found'}), 404
    
    user_data = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'avatar': user.avatar(),
        'created_at': user.created_at.isoformat()
    }
    return jsonify(user_data)


@bp.route('/users/<username>')
@jwt_required()
def get_user(username):
    """Returns the public profile of any user.
    """
    user = db.first_or_404(sa.select(User).where(User.username == username))

    # Return only public-safe information
    user_data = {
        'username': user.username,
        'avatar': user.avatar(),
        'created_at': user.created_at.isoformat()
    }
    return jsonify(user_data)


@bp.route('/hello')
def hello():
    return jsonify({"message": "Hello from the otherside!!!!!!!"})

# ------ What happens to the old routes? -------
# The logic for 'logout' is now handled by the client (React will just delete the token).
# The 'index' page is now the React app.
# The 'dashboard' page is also now part of the React app, which will fetch its data from
# new API endpoints you will create, like '/api/notes' and '/api/todolists'.