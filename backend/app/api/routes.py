from app import db
from app.api import bp
from app.forms import SignupForm
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import sqlalchemy as sa
from app.models import User, GenderEnum, Note


# ------ Authentication API Endpoints -------

@bp.route('/auth/register', methods=['POST'])
def register():
    """User registration endpoint.
    Expects a JSON body with user details.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad Request",
                        "message": "Request body must be valid JSON"}), 400
    
    # use form to validate incoming JSON data
    # `csrf_enabled=False` is important for an API
    form = SignupForm(data=data, csrf_enabled=False)
    
    if form.validate():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            email=form.email.data,
            gender=GenderEnum(form.gender.data)
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201
    else:  # i.e. validation failed
        return jsonify({"error": "Validation Error", "message": form.errors}), 422


@bp.route('/auth/login', methods=['POST'])
def login():
    """User login endpoint. Returns an access token.
    Expects JSON with username and password, returns a JWT.
    """
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = db.session.scalar(sa.select(User).where(User.username == data['username']))

    if user is None or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401  # 401 Unauthorized
    
    # Create the token. 'identity' can be anything unique to the user.
    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token)


# ------ User Data API Endpoints -------

@bp.route('/auth/me')
@jwt_required()
def get_me():
    """Returns profile of the currently authenticated user.
    """
    current_user_id = get_jwt_identity()  # Get the user's ID from the token
    user = db.session.get(User, current_user_id)

    if user is None:
        return jsonify({'error': 'User not found'}), 404
    
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'avatar': user.avatar(),
        'created_at': user.created_at.isoformat()
    }
    return jsonify(user_data)


# ------ Notes API Endpoints --------

@bp.route('/notes', methods=['POST'])
@jwt_required()
def create_note():
    """Creates a new note for the currently authenticated user.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    title = data.get('title')  # Can be None or an empty string
    content = data.get('content')  # Can be None

    if not title and not content:
        return jsonify({
            "error": "Validation Error",
            "message": "A note must have either a title or content."
        }), 400
    
    new_note = Note(
        title=title,
        content=content,
        author=user,
        group_id=data.get('group_id')  # Optional group assignment
    )
    db.session.add(new_note)
    db.session.commit()

    return jsonify({
        'id': new_note.id,
        'title': new_note.title,
        'content': new_note.content,
        'created_at': new_note.created_at.isoformat()
    }), 201


@bp.route('/notes', methods=['GET'])
@jwt_required()
def get_notes():
    """Retrieves all notes for the currently authenticated user.
    """
    current_user_id = get_jwt_identity()

    notes_query = db.session.execute(
        sa.select(Note).where(Note.user_id == current_user_id).order_by(Note.updated_at.desc())
    ).scalars().all()

    notes_list = [
        {
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'updated_at': note.updated_at.isoformat()
        }
        for note in notes_query
    ]

    return jsonify(notes_list)

# @bp.route('/hello')
# def hello():
#     return jsonify({"message": "Hello from the otherside!!!!!!!"})
