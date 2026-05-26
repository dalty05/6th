from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from models import db, User, Product, BlogPost, Testimonial, Statistic
from dotenv import load_dotenv
import os
from datetime import datetime
import pkgutil
import importlib.util
import ast

# Compatibility shim: provide missing attributes removed in Python 3.14+
# Provide pkgutil.get_loader and any legacy workarounds needed by old Werkzeug.
#
# IMPORTANT:
# Do NOT patch `ast.Str`. Werkzeug 3's routing compilation expects the real
# `ast.Str` node to exist. If your Python build doesn't include it, the right
# fix is dependency alignment (Werkzeug/Flask versions) and/or upgrading.

if not hasattr(pkgutil, 'get_loader'):
    def _get_loader(name):
        try:
            spec = importlib.util.find_spec(name)
            return spec.loader if spec is not None else None
        except Exception:
            return None
    pkgutil.get_loader = _get_loader


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

if not os.path.exists(dotenv_path):
    dotenv_path = os.path.join(os.path.dirname(__file__), 'dotenv.env')
load_dotenv(dotenv_path)

# Initialize Flask app FIRST
app = Flask(__name__, static_folder='../dist', static_url_path='')

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meru_dairy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FRONTEND_URL'] = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Email configuration (optional for now)

# Initialize extensions
CORS(app, supports_credentials=True)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import and register auth blueprint
from auth_routes import auth_bp
app.register_blueprint(auth_bp, url_prefix='/api')

# ========== PRODUCTS ROUTES ==========
@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'category': p.category,
        'description': p.description,
        'benefits': p.benefits,
        'packaging_sizes': p.packaging_sizes,
        'nutritional_info': p.nutritional_info,
        'ingredients': p.ingredients,
        'image_url': p.image_url,
        'featured': p.featured
    } for p in products])

@app.route('/api/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'category': product.category,
        'description': product.description,
        'benefits': product.benefits,
        'packaging_sizes': product.packaging_sizes,
        'nutritional_info': product.nutritional_info,
        'ingredients': product.ingredients,
        'image_url': product.image_url
    })

# ========== BLOG ROUTES ==========
@app.route('/api/blog', methods=['GET'])
def get_blog_posts():
    from flask import request

    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 6))
    featured_mode = request.args.get('mode', 'recent')

    base_q = BlogPost.query.filter_by(
        status='published'
    ).order_by(BlogPost.created_at.desc())

    posts = base_q.all()

    if not posts:
        return jsonify({
            "items": [],
            "total": 0,
            "page": page,
            "page_size": page_size
        })

    # Featured post
    featured = posts[:1]

    # Recent posts
    if len(posts) <= 1:
        recent = posts
    else:
        recent = posts[1:]

    # Select mode
    if featured_mode == 'featured':
        items_source = featured
    else:
        items_source = recent

    # Pagination
    total = len(items_source)
    start = (page - 1) * page_size
    end = start + page_size
    items = items_source[start:end]

    return jsonify({
        "items": [{
            'id': p.id,
            'title': p.title,
            'slug': p.slug,
            'excerpt': p.excerpt,
            'content': p.content,
            'featured_image': p.featured_image,
            'views': p.views,
            'created_at': p.created_at.isoformat() if p.created_at else None,
            'author': p.author.full_name if p.author else 'Admin'
        } for p in items],
        "total": total,
        "page": page,
        "page_size": page_size
    })




@app.route('/api/blog/<slug>', methods=['GET'])
def get_blog_post(slug):
    post = BlogPost.query.filter_by(slug=slug, status='published').first_or_404()
    post.views += 1
    db.session.commit()
    return jsonify({
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'featured_image': post.featured_image,
        'views': post.views,
        'created_at': post.created_at.isoformat() if post.created_at else None,
        'author': post.author.full_name if post.author else 'Admin'
    })

# ========== TESTIMONIALS ROUTES ==========
@app.route('/api/testimonials', methods=['GET'])
def get_testimonials():
    testimonials = Testimonial.query.filter_by(is_approved=True).order_by(Testimonial.created_at.desc()).limit(6).all()
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'role': t.role,
        'content': t.content,
        'rating': t.rating
    } for t in testimonials])

# ========== STATISTICS ROUTES ==========
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<path:filename>', methods=['GET'])
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    from flask import request

    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400

    file = request.files['file']
    folder = request.form.get('folder', 'general')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    safe_folder = secure_filename(folder)
    target_dir = os.path.join(app.config['UPLOAD_FOLDER'], safe_folder)
    os.makedirs(target_dir, exist_ok=True)

    filename = secure_filename(file.filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    filename = f"{timestamp}_{filename}"
    filepath = os.path.join(target_dir, filename)
    file.save(filepath)

    return jsonify({'url': f"/uploads/{safe_folder}/{filename}"}), 201

@app.route('/api/admin/products/<int:id>/image', methods=['POST'])
def upload_product_image(id):
    from flask import request
    product = Product.query.get_or_404(id)

    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    target_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'products')
    os.makedirs(target_dir, exist_ok=True)

    filename = secure_filename(file.filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    filename = f"{timestamp}_{filename}"
    filepath = os.path.join(target_dir, filename)
    file.save(filepath)

    product.image_url = f"/uploads/products/{filename}"
    db.session.commit()

    return jsonify({'url': product.image_url}), 201

@app.route('/api/admin/blog/<int:id>/image', methods=['POST'])
# Backward-compat route (frontend may call plural /blogs)
@app.route('/api/admin/blogs/<int:id>/image', methods=['POST'])
def upload_blog_image(id):
    from flask import request
    post = BlogPost.query.get_or_404(id)

    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    target_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'blogs')
    os.makedirs(target_dir, exist_ok=True)

    filename = secure_filename(file.filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    filename = f"{timestamp}_{filename}"
    filepath = os.path.join(target_dir, filename)
    file.save(filepath)

    post.featured_image = f"/uploads/blogs/{filename}"
    db.session.commit()

    return jsonify({'url': post.featured_image}), 201

# ========== ADMIN ROUTES (for managing products and blog) ==========
@app.route('/api/admin/products', methods=['POST'])
def create_product():
    from flask import request
    data = request.json
    product = Product(
        name=data['name'],
        category=data.get('category'),
        description=data['description'],
        benefits=data.get('benefits'),
        packaging_sizes=data.get('packaging_sizes'),
        nutritional_info=data.get('nutritional_info'),
        ingredients=data.get('ingredients'),
        image_url=data.get('image_url'),
        featured=data.get('featured', False)
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Product created', 'id': product.id}), 201

@app.route('/api/admin/products/<int:id>', methods=['PUT'])
def update_product(id):
    from flask import request
    product = Product.query.get_or_404(id)
    data = request.json
    for key, value in data.items():
        if hasattr(product, key):
            setattr(product, key, value)
    product.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Product updated'})

@app.route('/api/admin/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'})

@app.route('/api/admin/blog', methods=['POST'])
def create_blog_post():
    from flask import request
    data = request.json
    post = BlogPost(
        title=data['title'],
        slug=data['slug'],
        excerpt=data.get('excerpt'),
        content=data['content'],
        featured_image=data.get('featured_image'),
        status=data.get('status', 'published')
    )
    db.session.add(post)
    db.session.commit()
    return jsonify({'message': 'Blog post created', 'id': post.id}), 201

@app.route('/api/admin/blog/<int:id>', methods=['PUT'])
def update_blog_post(id):
    from flask import request
    post = BlogPost.query.get_or_404(id)
    data = request.json
    for key, value in data.items():
        if hasattr(post, key):
            setattr(post, key, value)
    post.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Blog post updated'})

@app.route('/api/admin/blog/<int:id>', methods=['DELETE'])
def delete_blog_post(id):
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Blog post deleted'})

# Serve frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    if path and path.split('.')[-1] in ['js', 'css', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'json']:
        try:
            return send_from_directory('../dist', path)
        except:
            pass
    return send_from_directory('../dist', 'index.html')

@app.errorhandler(404)
def not_found(error):
    return send_from_directory('../dist', 'index.html')

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

# Create app context and initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)