from flask import Flask
from flask_cors import CORS
from db import init_db
from routes.auth import auth_bp

app = Flask(__name__)
CORS(app)

# Load configuration
app.config.from_object('config.Config')

# Initialize database
init_db(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')

@app.route('/')
def index():
    return {'message': 'API is running'}

if __name__ == '__main__':
    app.run(debug=False)
