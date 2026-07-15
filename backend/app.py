
from flask import Flask, send_from_directory, jsonify, request, send_file
from flask_cors import CORS
from flask_login import LoginManager
from werkzeug.utils import secure_filename
from models import  db, User
from dotenv import load_dotenv
import os
from datetime import datetime
import pkgutil
import importlib.util
from middleware import permission_middleware
from functools import wraps
from flask import jsonify
from flask_login import login_user, logout_user, login_required
from flask_mail import Mail
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3
from sqlalchemy.exc import OperationalError
import time

# Import unified blueprints
from admin_routes import admin_bp
from public_routes import public_bp
from auth_routes import auth_bp

if not hasattr(pkgutil, 'get_loader'):
    def _get_loader(name):
        try:
            spec = importlib.util.find_spec(name)
            return spec.loader if spec is not None else None
        except Exception:
            return None
    pkgutil.get_loader = _get_loader

# ============================================================================
# APP INITIALIZATION
# ============================================================================

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(dotenv_path):
    dotenv_path = os.path.join(os.path.dirname(__file__), 'dotenv.env')
load_dotenv(dotenv_path)

app = Flask(__name__, static_folder='../dist', static_url_path='')

# ============================================================================
# CONFIGURATION
# ============================================================================

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meru_dairy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FRONTEND_URL'] = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', '0') == '1'

app.config['STATIC_FOLDER'] = 'static'
app.config['STATIC_URL_PATH'] = '/static'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# ============================================================================
# EXTENSIONS INITIALIZATION
# ============================================================================

CORS(app, supports_credentials=True)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.test_login'

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({'error': 'Authentication required'}), 401

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

mail = Mail()

# ============================================================================
# BLUEPRINT REGISTRATION
# ============================================================================

#  Register blueprints
app.register_blueprint(admin_bp)          # admin endpoints
app.register_blueprint(public_bp)         # / public endpoints
app.register_blueprint(auth_bp, url_prefix='/api')  # Auth endpoints

# ============================================================================
# MIDDLEWARE
# ============================================================================

@app.before_request
def check_permissions():
    return permission_middleware()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def allowed_file(filename):
    """Check if file type is allowed for upload"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

@app.teardown_appcontext
def shutdown_session(exception=None):
    """Close database session at the end of each request"""
    if exception:
        db.session.rollback()
    db.session.remove()

def with_retry(func, max_retries=3, delay=0.5):
    """Retry a function if database is locked"""
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    db.session.rollback()
                    time.sleep(delay * (attempt + 1))
                    continue
                raise
        return None
    return wrapper

# ============================================================================
# STATIC FILE ROUTES
# ============================================================================

@app.route('/uploads/<path:filename>', methods=['GET'])
def serve_upload(filename):
    """Serve uploaded files"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    return jsonify({'error': f'File not found: {filename}'}), 404

@app.route('/static/qr_codes/<path:filename>')
def serve_qr_code(filename):
    """Serve QR code images"""
    try:
        return send_from_directory('static/qr_codes', filename)
    except FileNotFoundError:
        return jsonify({'error': 'QR code not found'}), 404

@app.route('/backend-static/<path:filename>')
def serve_backend_static(filename):
    """Serve backend static files"""
    try:
        return send_from_directory('static', filename)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Meru Dairy API is running'
    }), 200

# ============================================================================
# FRONTEND SERVING
# ============================================================================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve Vue.js frontend"""
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    
    # Check for static files
    if path and '.' in path and path.split('.')[-1] in ['js', 'css', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'json', 'ico']:
        try:
            return send_from_directory('../dist', path)
        except:
            pass
    
    return send_from_directory('../dist', 'index.html')

@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({
            "error": "Route Not Found",
            "message": f"API route not found: {request.path}"
        }), 404
    return send_from_directory('../dist', 'index.html')

@app.errorhandler(500)
def internal_error(error):
   
    import traceback
    traceback.print_exc()
    return jsonify({'error': 'Internal server error', 'details': str(error)}), 500

@app.route('/favicon.ico')
def favicon():
    return '', 204


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    print("\n" + "=" * 60)

    print("SYSTEM UP AND RUNNING")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)