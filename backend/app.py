from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Product, BlogPost, Testimonial, Statistic
from dotenv import load_dotenv
import os
from datetime import datetime

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

# Email configuration (optional for now)
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() in ('1', 'true', 'yes')
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() in ('1', 'true', 'yes')
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'oyigodalton@gmail.com')

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
    posts = BlogPost.query.filter_by(status='published').order_by(BlogPost.created_at.desc()).all()
    return jsonify([{
        'id': p.id,
        'title': p.title,
        'slug': p.slug,
        'excerpt': p.excerpt,
        'content': p.content,
        'featured_image': p.featured_image,
        'views': p.views,
        'created_at': p.created_at.isoformat() if p.created_at else None,
        'author': p.author.full_name if p.author else 'Admin'
    } for p in posts])

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
@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    stats = Statistic.query.order_by(Statistic.order).all()
    return jsonify([{
        'label': s.label,
        'value': s.value,
        'suffix': s.suffix
    } for s in stats])

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