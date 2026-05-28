from flask import Flask, send_from_directory, jsonify, request
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

# ============================================================================
# PYTHON 3.14+ COMPATIBILITY SHIMS
# ============================================================================
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
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# CORS Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# ============================================================================
# EXTENSIONS INITIALIZATION
# ============================================================================
CORS(app, supports_credentials=True)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ============================================================================
# BLUEPRINT REGISTRATION
# ============================================================================
from auth_routes import auth_bp
app.register_blueprint(auth_bp, url_prefix='/api')

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def allowed_file(filename):
    """Check if file type is allowed for upload"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================================================
# PUBLIC API ROUTES
# ============================================================================

# ---------------------- HEALTH CHECK ----------------------
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Meru Dairy API is running'
    }), 200

# ---------------------- STATISTICS (CACHED) ----------------------
@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get website statistics - cached for better performance"""
    try:
        stats = Statistic.query.order_by(Statistic.order).all()
        return jsonify([{
            'id': s.id,
            'label': s.label,
            'value': s.value,
            'suffix': s.suffix
        } for s in stats])
    except Exception as e:
        print(f"Error fetching statistics: {e}")
        return jsonify([]), 200  # Return empty array instead of error

# ---------------------- PRODUCTS ----------------------
@app.route('/api/products', methods=['GET'])
def get_products():
    """
    Get products with pagination, filtering, and search
    Query params:
    - page: int (default: 1)
    - per_page: int (default: 12)
    - category: string (optional)
    - featured: boolean (optional)
    - search: string (optional)
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        category = request.args.get('category', None)
        featured_only = request.args.get('featured', False, type=bool)
        search = request.args.get('search', None)
        
        # Ensure valid pagination values
        page = max(1, page)
        per_page = min(50, max(1, per_page))  # Max 50 items per page
        
        # Build query
        query = Product.query
        
        # Apply filters
        if category and category != 'All' and category != '':
            query = query.filter_by(category=category)
        
        if featured_only:
            query = query.filter_by(featured=True)
        
        if search and search.strip():
            search_term = f"%{search.strip()}%"
            query = query.filter(
                db.or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.benefits.ilike(search_term)
                )
            )
        
        # Paginate
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': [{
                'id': p.id,
                'name': p.name,
                'category': p.category,
                'description': p.description[:200] + '...' if len(p.description) > 200 else p.description,
                'benefits': p.benefits,
                'packaging_sizes': p.packaging_sizes,
                'nutritional_info': p.nutritional_info,
                'ingredients': p.ingredients,
                'image_url': p.image_url,
                'featured': p.featured,
                'created_at': p.created_at.isoformat() if p.created_at else None
            } for p in paginated.items],
            'pagination': {
                'current_page': paginated.page,
                'total_pages': paginated.pages,
                'total_items': paginated.total,
                'items_per_page': per_page,
                'has_next': paginated.has_next,
                'has_prev': paginated.has_prev
            }
        })
    except Exception as e:
        print(f"Error in get_products: {e}")
        return jsonify({'error': 'Failed to fetch products'}), 500

@app.route('/api/products/featured', methods=['GET'])
def get_featured_products():
    """Get featured products for homepage (no pagination needed)"""
    try:
        limit = request.args.get('limit', 6, type=int)
        limit = min(12, max(1, limit))
        
        products = Product.query.filter_by(featured=True).limit(limit).all()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'category': p.category,
            'description': p.description[:120] + '...' if len(p.description) > 120 else p.description,
            'image_url': p.image_url,
            'featured': p.featured,
            'packaging_sizes': p.packaging_sizes
        } for p in products])
    except Exception as e:
        print(f"Error in get_featured_products: {e}")
        return jsonify([]), 200

@app.route('/api/products/<int:id>', methods=['GET'])
def get_product(id):
    """Get single product by ID"""
    try:
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
            'image_url': product.image_url,
            'featured': product.featured
        })
    except Exception as e:
        print(f"Error in get_product: {e}")
        return jsonify({'error': 'Product not found'}), 404

@app.route('/api/products/categories', methods=['GET'])
def get_product_categories():
    """Get all unique product categories"""
    try:
        categories = db.session.query(Product.category).distinct().all()
        categories = [c[0] for c in categories if c[0]]
        return jsonify(['All'] + categories)
    except Exception as e:
        print(f"Error in get_product_categories: {e}")
        return jsonify(['All', 'Fresh Milk', 'Yoghurt', 'Lala', 'Ghee']), 200

# ========== BLOG ROUTES ==========
@app.route('/api/blog', methods=['GET'])
def get_blog_posts():
    """
    Get blog posts with pagination
    Query params:
    - page: int (default: 1)
    - per_page: int (default: 6)
    - simple: boolean (default: false) - if true, returns array without pagination
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 6, type=int)
        simple_mode = request.args.get('simple', 'false').lower() == 'true'
        
        print(f"Blog request - page: {page}, per_page: {per_page}, simple_mode: {simple_mode}")  # Debug
        
        # Validate pagination values
        page = max(1, page)
        per_page = min(20, max(1, per_page))
        
        # Build query - only published posts
        query = BlogPost.query.filter_by(status='published').order_by(BlogPost.created_at.desc())
        
        # SIMPLE MODE: Return array without pagination (for homepage initial load)
        if simple_mode:
            posts = query.limit(per_page).all()
            return jsonify([{
                'id': p.id,
                'title': p.title,
                'slug': p.slug,
                'excerpt': p.excerpt[:150] + '...' if p.excerpt and len(p.excerpt) > 150 else p.excerpt,
                'content': p.content[:200] + '...' if p.content and len(p.content) > 200 else p.content,
                'featured_image': p.featured_image,
                'views': p.views,
                'created_at': p.created_at.isoformat() if p.created_at else None,
                'author': p.author.full_name if p.author else 'Admin'
            } for p in posts])
        
        # PAGINATED MODE: Return with pagination object
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': [{
                'id': p.id,
                'title': p.title,
                'slug': p.slug,
                'excerpt': p.excerpt[:150] + '...' if p.excerpt and len(p.excerpt) > 150 else p.excerpt,
                'content': p.content[:200] + '...' if p.content and len(p.content) > 200 else p.content,
                'featured_image': p.featured_image,
                'views': p.views,
                'created_at': p.created_at.isoformat() if p.created_at else None,
                'author': p.author.full_name if p.author else 'Admin'
            } for p in paginated.items],
            'pagination': {
                'current_page': paginated.page,
                'total_pages': paginated.pages,
                'total_items': paginated.total,
                'items_per_page': per_page,
                'has_next': paginated.has_next,
                'has_prev': paginated.has_prev
            }
        })
        
    except Exception as e:
        print(f"Error in get_blog_posts: {e}")
        return jsonify([]), 200



@app.route('/api/blog/<slug>', methods=['GET'])
def get_blog_post(slug):
    """Get single blog post by slug"""
    try:
        post = BlogPost.query.filter_by(slug=slug, status='published').first_or_404()
        
        # Increment view count
        post.views += 1
        db.session.commit()
        
        return jsonify({
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'excerpt': post.excerpt,
            'content': post.content,
            'featured_image': post.featured_image,
            'views': post.views,
            'created_at': post.created_at.isoformat() if post.created_at else None,
            'updated_at': post.updated_at.isoformat() if post.updated_at else None,
            'author': post.author.full_name if post.author else 'Admin'
        })
    except Exception as e:
        print(f"Error in get_blog_post: {e}")
        return jsonify({'error': 'Post not found'}), 404

# ---------------------- TESTIMONIALS ----------------------
@app.route('/api/testimonials', methods=['GET'])
def get_testimonials():
    """Get approved testimonials"""
    try:
        limit = request.args.get('limit', 6, type=int)
        limit = min(12, max(1, limit))
        
        testimonials = Testimonial.query.filter_by(is_approved=True)\
            .order_by(Testimonial.created_at.desc())\
            .limit(limit).all()
        
        return jsonify([{
            'id': t.id,
            'name': t.name,
            'role': t.role,
            'content': t.content,
            'rating': t.rating,
            'created_at': t.created_at.isoformat() if t.created_at else None
        } for t in testimonials])
    except Exception as e:
        print(f"Error in get_testimonials: {e}")
        return jsonify([]), 200

# ============================================================================
# IMAGE UPLOAD ROUTES
# ============================================================================

@app.route('/uploads/<path:filename>', methods=['GET'])
def serve_upload(filename):
    """Serve uploaded files with caching headers"""
    try:
        response = send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        response.cache_control.max_age = 31536000  # 1 year cache
        response.cache_control.public = True
        return response
    except Exception:
        return jsonify({'error': 'File not found'}), 404

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Generic file upload endpoint"""
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
    """Upload image for a specific product"""
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
@app.route('/api/admin/blogs/<int:id>/image', methods=['POST'])
def upload_blog_image(id):
    """Upload image for a specific blog post"""
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

# ============================================================================
# ADMIN CRUD ROUTES
# ============================================================================

@app.route('/api/admin/products', methods=['POST'])
def create_product():
    """Create a new product (admin only)"""
    try:
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
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/products/<int:id>', methods=['PUT'])
def update_product(id):
    """Update an existing product (admin only)"""
    try:
        product = Product.query.get_or_404(id)
        data = request.json
        for key, value in data.items():
            if hasattr(product, key) and key not in ['id', 'created_at', 'updated_at']:
                setattr(product, key, value)
        product.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Product updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    """Delete a product (admin only)"""
    try:
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/blog', methods=['POST'])
def create_blog_post():
    """Create a new blog post (admin only)"""
    try:
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
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/blog/<int:id>', methods=['PUT'])
def update_blog_post(id):
    """Update an existing blog post (admin only)"""
    try:
        post = BlogPost.query.get_or_404(id)
        data = request.json
        for key, value in data.items():
            if hasattr(post, key) and key not in ['id', 'created_at', 'views']:
                setattr(post, key, value)
        post.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Blog post updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/blog/<int:id>', methods=['DELETE'])
def delete_blog_post(id):
    """Delete a blog post (admin only)"""
    try:
        post = BlogPost.query.get_or_404(id)
        db.session.delete(post)
        db.session.commit()
        return jsonify({'message': 'Blog post deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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
    
    # For all other routes, serve index.html (Vue Router)
    return send_from_directory('../dist', 'index.html')

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return send_from_directory('../dist', 'index.html')

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    print(f"Server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

with app.app_context():
    db.create_all()
    print("Database tables verified/created")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 MERU DAIRY BACKEND SERVER")
    print("=" * 60)
    print(f"📍 Server running at: http://localhost:5000")
    print(f"🔧 Debug mode: ON")
    print("\n📋 API Endpoints:")
    print("   GET  /api/health              - Health check")
    print("   GET  /api/statistics          - Get statistics")
    print("   GET  /api/products            - Get products (paginated)")
    print("   GET  /api/products/featured   - Get featured products")
    print("   GET  /api/products/<id>       - Get single product")
    print("   GET  /api/products/categories - Get product categories")
    print("   GET  /api/blog                - Get blog posts (paginated)")
    print("   GET  /api/blog/<slug>         - Get single blog post")
    print("   GET  /api/testimonials        - Get testimonials")
    print("   POST /api/upload              - Upload file")
    print("   POST /api/contact             - Send contact message")
    print("\n🔐 Auth Endpoints:")
    print("   POST /api/auth/register       - Register new admin")
    print("   POST /api/auth/login/step1    - Login step 1 (email/password)")
    print("   POST /api/auth/login/step2    - Login step 2 (OTP)")
    print("   POST /api/auth/forgot-password - Request password reset")
    print("   POST /api/auth/reset-password  - Reset password")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)