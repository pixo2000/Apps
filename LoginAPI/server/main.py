from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from functools import wraps
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up UTC timezone (compatible with all Python versions)
try:
    # For Python 3.11+
    UTC = datetime.UTC
except AttributeError:
    # For Python 3.10 and earlier
    UTC = datetime.timezone.utc

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'thisissecret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, default=False)

# Token authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

# Routes
@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if user already exists
    user = User.query.filter_by(email=data['email']).first()
    if user:
        return jsonify({'message': 'User already exists with this email'}), 409
    
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    new_user = User(
        public_id=str(uuid.uuid4()),
        name=data['name'],
        email=data['email'],
        password=hashed_password,
        registered_on=datetime.datetime.now(UTC)
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    auth = request.get_json()
    
    if not auth or not auth.get('email') or not auth.get('password'):
        return make_response('Missing login credentials', 401)
    
    user = User.query.filter_by(email=auth['email']).first()
    
    if not user:
        return make_response('User not found', 401)
    
    if check_password_hash(user.password, auth['password']):
        token = jwt.encode({
            'public_id': user.public_id,
            'exp': datetime.datetime.now(UTC) + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            'token': token,
            'user': {
                'name': user.name,
                'email': user.email,
                'admin': user.admin
            }
        })
    
    return make_response('Invalid password', 401)

@app.route('/api/user', methods=['GET'])
@token_required
def get_user_profile(current_user):
    user_data = {
        'public_id': current_user.public_id,
        'name': current_user.name,
        'email': current_user.email,
        'admin': current_user.admin,
        'registered_on': current_user.registered_on
    }
    
    return jsonify(user_data)

@app.route('/api/user', methods=['PUT'])
@token_required
def update_user_profile(current_user):
    data = request.get_json()
    
    if 'name' in data:
        current_user.name = data['name']
    
    if 'email' in data:
        # Check if email is already taken
        if User.query.filter_by(email=data['email']).first() and data['email'] != current_user.email:
            return jsonify({'message': 'Email already in use'}), 409
        current_user.email = data['email']
    
    if 'password' in data:
        current_user.password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    db.session.commit()
    
    return jsonify({'message': 'User profile updated successfully'})

@app.route('/api/password-reset-request', methods=['POST'])
def reset_password_request():
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({'message': 'Email is required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        # Don't reveal that the user doesn't exist
        return jsonify({'message': 'If your email is registered, you will receive a password reset link'}), 200
    
    # Generate reset token
    reset_token = str(uuid.uuid4())
    user.reset_token = reset_token
    user.reset_token_expiry = datetime.datetime.now(UTC) + datetime.timedelta(hours=1)
    
    db.session.commit()
    
    # Create reset link
    reset_link = f"http://localhost:8000/reset-password/{reset_token}"
    
    # For development: Return token directly if email is not configured
    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        # Debug mode - only for development!
        return jsonify({
            'message': 'Email not configured. Here is your reset token (for development only)',
            'token': reset_token,
            'reset_link': reset_link
        }), 200
    
    # Send email
    try:
        msg = Message(
            'Password Reset Request',
            sender=app.config['MAIL_USERNAME'],
            recipients=[user.email]
        )
        msg.body = f'Hi {user.name},\n\nTo reset your password, please click on the following link:\n\n{reset_link}\n\nThis link will expire in 1 hour.\n\nIf you did not request this password reset, please ignore this email.'
        mail.send(msg)
        
        return jsonify({'message': 'If your email is registered, you will receive a password reset link'}), 200
    except Exception as e:
        # Log the actual error for debugging
        print(f"Email error: {str(e)}")
        # Rollback the token changes since email failed
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        return jsonify({
            'message': 'Could not send email, please try again later',
            'error': str(e)
        }), 500

@app.route('/api/password-reset/<token>', methods=['POST'])
def reset_password(token):
    data = request.get_json()
    
    if not data or not data.get('password'):
        return jsonify({'message': 'New password is required'}), 400
    
    user = User.query.filter_by(reset_token=token).first()
    
    if not user:
        return jsonify({'message': 'Invalid or expired reset link'}), 400
    
    # Check if token is expired
    if user.reset_token_expiry < datetime.datetime.now(UTC):
        return jsonify({'message': 'Reset link has expired'}), 400
    
    # Update password
    user.password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    user.reset_token = None
    user.reset_token_expiry = None
    
    db.session.commit()
    
    return jsonify({'message': 'Password has been reset successfully'}), 200

@app.route('/api/admin/users', methods=['GET'])
@token_required
def get_all_users(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that action!'}), 403
    
    users = User.query.all()
    output = []
    
    for user in users:
        user_data = {
            'public_id': user.public_id,
            'name': user.name,
            'email': user.email,
            'admin': user.admin,
            'registered_on': user.registered_on
        }
        output.append(user_data)
    
    return jsonify({'users': output})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
