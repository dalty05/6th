from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from models import db, User, Product, BlogPost, Testimonial, Statistic


import os
from werkzeug.utils import secure_filename
from flask import request, jsonify, send_from_directory
from datetime import datetime



app = Flask(__name__, static_folder='../dist', static_url_path='')
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meru_dairy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

CORS(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


# Create upload directories
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'products'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'blogs'), exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# API Routes

# Products
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

@app.route('/api/admin/products', methods=['POST'])
@login_required
def create_product():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
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


# Update product routes to handle image uploads
@app.route('/api/admin/products/<int:id>/image', methods=['POST'])
@login_required
def upload_product_image(id):
    """Upload image for a specific product"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'products')
        os.makedirs(upload_path, exist_ok=True)
        
        filepath = os.path.join(upload_path, filename)
        file.save(filepath)
        
        image_url = f'/uploads/products/{filename}'
        
        # Update product with new image URL
        product = Product.query.get_or_404(id)
        product.image_url = image_url
        db.session.commit()
        
        return jsonify({'url': image_url}), 200
    
    return jsonify({'error': 'Invalid file type'}), 400



@app.route('/api/admin/products/<int:id>', methods=['PUT'])
@login_required
def update_product(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    product = Product.query.get_or_404(id)
    data = request.json
    for key, value in data.items():
        if hasattr(product, key):
            setattr(product, key, value)
    product.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Product updated'})

@app.route('/api/admin/products/<int:id>', methods=['DELETE'])
@login_required
def delete_product(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'})

# Blog Posts
@app.route('/api/blog', methods=['GET'])
def get_blog_posts():
    posts = BlogPost.query.filter_by(status='published').order_by(BlogPost.created_at.desc()).all()
    return jsonify([{
        'id': p.id,
        'title': p.title,
        'slug': p.slug,
        'excerpt': p.excerpt,
        'featured_image': p.featured_image,
        'views': p.views,
        'created_at': p.created_at.isoformat(),
        'author': p.author.username if p.author else 'Admin'
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
        'created_at': post.created_at.isoformat(),
        'author': post.author.username if post.author else 'Admin'
    })

@app.route('/api/admin/blog', methods=['POST'])
@login_required
def create_blog_post():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    post = BlogPost(
        title=data['title'],
        slug=data['slug'],
        excerpt=data.get('excerpt'),
        content=data['content'],
        featured_image=data.get('featured_image'),
        author_id=current_user.id,
        status=data.get('status', 'published')
    )
    db.session.add(post)
    db.session.commit()
    return jsonify({'message': 'Blog post created', 'id': post.id}), 201



# Update blog image upload
@app.route('/api/admin/blog/<int:id>/image', methods=['POST'])
@login_required
def upload_blog_image(id):
    """Upload featured image for a specific blog post"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'blogs')
        os.makedirs(upload_path, exist_ok=True)
        
        filepath = os.path.join(upload_path, filename)
        file.save(filepath)
        
        image_url = f'/uploads/blogs/{filename}'
        
        # Update blog post with new image URL
        post = BlogPost.query.get_or_404(id)
        post.featured_image = image_url
        db.session.commit()
        
        return jsonify({'url': image_url}), 200
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/admin/blog/<int:id>', methods=['PUT'])
@login_required
def update_blog_post(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    post = BlogPost.query.get_or_404(id)
    data = request.json
    for key, value in data.items():
        if hasattr(post, key):
            setattr(post, key, value)
    post.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Blog post updated'})

@app.route('/api/admin/blog/<int:id>', methods=['DELETE'])
@login_required
def delete_blog_post(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Blog post deleted'})

# Testimonials
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

# Statistics
@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    stats = Statistic.query.order_by(Statistic.order).all()
    return jsonify([{
        'label': s.label,
        'value': s.value,
        'suffix': s.suffix
    } for s in stats])

# Image Upload

@app.route('/api/upload', methods=['POST'])
@login_required
def upload_image():
    """Upload an image file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # Secure the filename and add timestamp to avoid collisions
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        # Determine folder based on type
        folder = request.form.get('folder', 'general')
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_path, exist_ok=True)
        
        filepath = os.path.join(upload_path, filename)
        file.save(filepath)
        
        # Return the URL path for the image
        image_url = f'/uploads/{folder}/{filename}'
        return jsonify({'url': image_url}), 200
    
    return jsonify({'error': 'Invalid file type'}), 400

# Serve uploaded files
@app.route('/uploads/<folder>/<filename>')
def uploaded_file(folder, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], folder), filename)
 




# Authentication
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and check_password_hash(user.password_hash, data.get('password')):
        login_user(user)
        return jsonify({'message': 'Login successful', 'is_admin': user.is_admin}), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/admin/logout', methods=['POST'])
@login_required
def admin_logout():
    logout_user()
    return jsonify({'message': 'Logged out'}), 200

@app.route('/api/admin/check', methods=['GET'])
def check_auth():
    if current_user.is_authenticated:
        return jsonify({'is_admin': current_user.is_admin}), 200
    return jsonify({'is_admin': False}), 200

# Serve Vue App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# Initialize database
@app.cli.command('init-db')
def init_db_command():
    """Initialize the database."""
    db.create_all()
    
    # Create admin user if not exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
    
    # Create sample statistics
    if Statistic.query.count() == 0:
        stats = [
            Statistic(label='Our Farmers', value='120,000', suffix='+', order=1),
            Statistic(label='Cooperative Societies', value='120', suffix='+', order=2),
            Statistic(label='Litres of Milk Processed per day', value='600,000', suffix='+', order=3),
            Statistic(label='Customers Served', value='10,000,000', suffix='+', order=4)
        ]
        for stat in stats:
            db.session.add(stat)
    
    db.session.commit()
    print('Database initialized!')

if __name__ == '__main__':
    app.run(debug=True, port=5000)