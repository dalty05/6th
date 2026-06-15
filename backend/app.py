from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from email_service import email_service
from models import NewsletterSubscriber, db, User, Product, BlogPost, Testimonial, Statistic
from dotenv import load_dotenv
import os
from datetime import datetime
import pkgutil
import importlib.util
from job_routes import job_bp
from permission_service import ROLE_PERMISSIONS
from middleware import permission_middleware

import pkgutil
import importlib.util


from permission_routes import permission_bp

from blog_routes import blog_bp




import re
from contact_routes import contact_bp

from referral_routes import referral_bp



from functools import wraps
from flask import jsonify
from flask_login import current_user





from flask_login import login_user, logout_user, login_required, current_user


from settings_routes import settings_bp




from permission_routes import permission_bp
from user_management_routes import user_mgmt_bp


from referral_routes import referral_bp
from notification_routes import notification_bp
from activity_routes import activity_bp

from outlet_routes import outlet_bp



# Add with other imports
from settings_routes import settings_bp








if not hasattr(pkgutil, 'get_loader'):
    def _get_loader(name):
        try:
            spec = importlib.util.find_spec(name)
            return spec.loader if spec is not None else None
        except Exception:
            return None
    pkgutil.get_loader = _get_loader

# APP INITIALIZATION

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(dotenv_path):
    dotenv_path = os.path.join(os.path.dirname(__file__), 'dotenv.env')
load_dotenv(dotenv_path)

app = Flask(__name__, static_folder='../dist', static_url_path='')


# CONFIGURATION


app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meru_dairy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FRONTEND_URL'] = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size



@app.before_request
def check_permissions():
    return permission_middleware()



# permision blueprints
app.register_blueprint(permission_bp, url_prefix='/api')
app.register_blueprint(user_mgmt_bp, url_prefix='/api')



app.register_blueprint(referral_bp, url_prefix='/api')
app.register_blueprint(notification_bp, url_prefix='/api')
app.register_blueprint(activity_bp, url_prefix='/api')


app.register_blueprint(settings_bp, url_prefix='/api')
app.register_blueprint(contact_bp, url_prefix='/api')
app.register_blueprint(job_bp, url_prefix='/api')
app.register_blueprint(outlet_bp, url_prefix='/api')

app.register_blueprint(blog_bp, url_prefix='/api')



# CORS Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# ============================================================================
# EXTENSIONS INITIALIZATION
# ============================================================================
CORS(app, supports_credentials=True)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.test_login'

# For API calls we generally want JSON 401/403 instead of redirects
@login_manager.unauthorized_handler
def unauthorized():
    from flask import jsonify
    return jsonify({'error': 'Authentication required'}), 401


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

@app.route('/api/debug/permissions', methods=['GET'])
@login_required
def debug_permissions():
    """Get current user's permissions for frontend"""
    from permission_service import has_permission
    
    resources = ['products', 'blog', 'jobs', 'outlets', 'users', 'partners', 'referrals', 'statistics', 'settings', 'contacts']
    actions = ['create', 'read', 'update', 'delete']
    
    permissions = {}
    for resource in resources:
        permissions[resource] = {}
        for action in actions:
            permissions[resource][action] = has_permission(current_user, resource, action)
    
    return jsonify({
        'user_id': current_user.id,
        'email': current_user.email,
        'role': current_user.role,
        'permissions': permissions
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
    """Get blog posts with pagination - PUBLIC"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 6, type=int)
        simple_mode = request.args.get('simple', 'false').lower() == 'true'
        
        page = max(1, page)
        per_page = min(20, max(1, per_page))
        
        # Only show published posts to public
        query = BlogPost.query.filter_by(status='published').order_by(BlogPost.created_at.desc())
        
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
# IMAGE UPLOAD ROUTES (Enhanced)
# ============================================================================
# Add these routes to app.py

# ========== IMAGE UPLOAD ROUTES ==========

@app.route('/uploads/<path:filename>', methods=['GET'])
def serve_upload(filename):
    """Serve uploaded files with debug"""
    import os
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    print(f"Looking for: {filepath}")
    print(f"File exists: {os.path.exists(filepath)}")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    
    if os.path.exists(filepath):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    else:
        return jsonify({'error': f'File not found: {filename}'}), 404

@app.route('/api/upload', methods=['POST'])
@login_required

def upload_file():

    """Generic file upload endpoint"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400
    
    file = request.files['file']
    folder = request.form.get('folder', 'general')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': f'File type not allowed'}), 400
    
    # Create folder if not exists
    safe_folder = secure_filename(folder)
    target_dir = os.path.join(app.config['UPLOAD_FOLDER'], safe_folder)
    os.makedirs(target_dir, exist_ok=True)
    
    # Generate unique filename
    original_filename = secure_filename(file.filename)
    name, ext = os.path.splitext(original_filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{name}{ext}"
    filepath = os.path.join(target_dir, filename)
    file.save(filepath)
    
    image_url = f"/uploads/{safe_folder}/{filename}"
    
    return jsonify({
        'url': image_url,
        'filename': filename,
        'message': 'File uploaded successfully'
    }), 201

# Product Image Upload (singular, not plural)
@app.route('/api/admin/product/<int:id>/upload-image', methods=['POST'])
@login_required

def upload_product_image(id):

    """Upload image directly to a product"""
    product = Product.query.get_or_404(id)
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Create product images folder
    target_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'products')
    os.makedirs(target_dir, exist_ok=True)
    
    # Generate unique filename
    original_filename = secure_filename(file.filename)
    name, ext = os.path.splitext(original_filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"product_{id}_{timestamp}_{name}{ext}"
    filepath = os.path.join(target_dir, filename)
    file.save(filepath)
    
    # Delete old image if exists
    if product.image_url:
        old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], product.image_url.replace('/uploads/', ''))
        if os.path.exists(old_filepath):
            os.remove(old_filepath)
    
    product.image_url = f"/uploads/products/{filename}"
    db.session.commit()
    
    return jsonify({
        'url': product.image_url,
        'message': 'Image uploaded successfully'
    }), 200

# Blog Image Upload (singular, not plural)
@app.route('/api/admin/blog/<int:id>/upload-image', methods=['POST'])
@login_required

def upload_blog_image(id):

    """Upload image directly to a blog post"""
    post = BlogPost.query.get_or_404(id)
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Create blog images folder
    target_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'blogs')
    os.makedirs(target_dir, exist_ok=True)
    
    # Generate unique filename
    original_filename = secure_filename(file.filename)
    name, ext = os.path.splitext(original_filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"blog_{id}_{timestamp}_{name}{ext}"
    filepath = os.path.join(target_dir, filename)
    file.save(filepath)
    
    # Delete old image if exists
    if post.featured_image:
        old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], post.featured_image.replace('/uploads/', ''))
        if os.path.exists(old_filepath):
            os.remove(old_filepath)
    
    post.featured_image = f"/uploads/blogs/{filename}"
    db.session.commit()
    
    return jsonify({
        'url': post.featured_image,
        'message': 'Image uploaded successfully'
    }), 200

# Also support plural versions for backward compatibility
@app.route('/api/admin/products/<int:id>/upload-image', methods=['POST'])
@login_required
def upload_product_image_plural(id):
    """Plural version for backward compatibility"""
    return upload_product_image(id)

@app.route('/api/admin/blogs/<int:id>/upload-image', methods=['POST'])
@login_required
def upload_blog_image_plural(id):
    """Plural version for backward compatibility"""
    return upload_blog_image(id)

# Newsletter subscription endpoint
@app.route('/api/newsletter/subscribe', methods=['POST'])
def subscribe_newsletter():
    """Subscribe a user to the newsletter"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        email = data.get('email', '').lower().strip()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if already subscribed
        existing = NewsletterSubscriber.query.filter_by(email=email).first()
        if existing:
            return jsonify({'message': 'Email already subscribed'}), 200
        
        # Create new subscriber
        subscriber = NewsletterSubscriber(
            name=name,
            email=email,
            subscribed_at=datetime.utcnow(),
            is_active=True
        )
        db.session.add(subscriber)
        db.session.commit()
        
        # Optional: Send welcome email
        # email_service.send_welcome_newsletter(name, email)
        
        return jsonify({'message': 'Subscribed successfully'}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error in subscribe_newsletter: {e}")
        return jsonify({'error': str(e)}), 500







# ============================================================================
# ADMIN CRUD ROUTES
# ============================================================================



# NOTE: permission enforcement is implemented in `permission_service.py`.
# `require_permission` is imported from there; do not redefine it here.





# ========== ADMIN PRODUCTS MANAGEMENT ROUTES ==========

@app.route('/api/admin/products', methods=['GET'])
@login_required

def admin_get_products():
    """Get all products for admin panel"""
    try:
        products = Product.query.order_by(Product.created_at.desc()).all()
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
            'featured': p.featured,
            'is_active': True,  # Assuming all products are active by default
            'created_at': p.created_at.isoformat() if p.created_at else None,
            'updated_at': p.updated_at.isoformat() if p.updated_at else None
        } for p in products]), 200
    except Exception as e:
        print(f"Error in admin_get_products: {e}")
        return jsonify([]), 200




@app.route('/api/admin/products', methods=['POST'])
@login_required

def admin_create_product():
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
@login_required

def admin_update_product(id):
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
@login_required

def admin_delete_product(id):
    """Delete a product (admin only)"""
    try:
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



# ========== ADMIN BLOG ROUTES ==========

# @app.route('/api/admin/blog', methods=['GET'])
# @login_required
# @require_permission('blog', 'create')
# def get_admin_blog_posts():
#     """Get all blog posts for admin panel (with author info)"""
#     try:
#         # Super admin sees all, regular admin sees only their own
#         if current_user.role == 'super_admin':
#             posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
#         else:
#             posts = BlogPost.query.filter_by(author_id=current_user.id).order_by(BlogPost.created_at.desc()).all()
        
#         return jsonify([{
#             'id': p.id,
#             'title': p.title,
#             'slug': p.slug,
#             'excerpt': p.excerpt,
#             'content': p.content,
#             'featured_image': p.featured_image,
#             'views': p.views,
#             'status': p.status,
#             'created_at': p.created_at.isoformat() if p.created_at else None,
#             'updated_at': p.updated_at.isoformat() if p.updated_at else None,
#             'author': p.author.full_name if p.author else 'Admin',
#             'author_id': p.author_id,
#             'can_edit': current_user.role == 'super_admin' or p.author_id == current_user.id
#         } for p in posts]), 200
#     except Exception as e:
#         print(f"Error in get_admin_blog_posts: {e}")
#         return jsonify([]), 200



# @app.route('/api/admin/blog', methods=['POST'])
# @login_required
# @require_permission('blog', 'create')
# def create_blog_post():
#     """Create a new blog post"""
#     try:
#         data = request.json
        
#         # Validate required fields
#         if not data.get('title'):
#             return jsonify({'error': 'Title is required'}), 400
#         if not data.get('slug'):
#             return jsonify({'error': 'Slug is required'}), 400
#         if not data.get('content'):
#             return jsonify({'error': 'Content is required'}), 400
        
#         # Check if slug already exists
#         existing = BlogPost.query.filter_by(slug=data['slug']).first()
#         if existing:
#             return jsonify({'error': 'Slug already exists. Please use a different slug.'}), 400
        
#         post = BlogPost(
#             title=data['title'],
#             slug=data['slug'],
#             excerpt=data.get('excerpt', ''),
#             content=data['content'],
#             featured_image=data.get('featured_image', ''),
#             status=data.get('status', 'draft'),  # Default to draft
#             author_id=current_user.id  # Set author to current user
#         )
        
#         db.session.add(post)
#         db.session.commit()
        
#         # Log activity
#         from activity_routes import log_activity
#         log_activity(
#             user_id=current_user.id,
#             user_name=current_user.full_name,
#             action='create',
#             resource_type='blog',
#             resource_id=post.id,
#             description=f'Created blog post: {post.title}'
#         )
        
#         return jsonify({'message': 'Blog post created', 'id': post.id}), 201
        
#     except Exception as e:
#         db.session.rollback()
#         print(f"Error creating blog post: {str(e)}")
#         return jsonify({'error': str(e)}), 500



# #  update_blog_post function

# @app.route('/api/admin/blog/<int:id>', methods=['PUT'])
# @login_required
# @require_permission('blog', 'update')
# def update_blog_post(id):
#     """Update an existing blog post (owner or super admin only)"""
#     try:
#         post = BlogPost.query.get_or_404(id)
        
#         # Check permission: only author or super admin can edit
#         if current_user.role != 'super_admin' and post.author_id != current_user.id:
#             return jsonify({'error': 'You can only edit your own blog posts'}), 403
        
#         data = request.json
        
#         # Update allowed fields
#         allowed_fields = ['title', 'slug', 'excerpt', 'content', 'featured_image', 'status']
        
#         for key, value in data.items():
#             if key in allowed_fields and hasattr(post, key):
#                 setattr(post, key, value)
        
#         post.updated_at = datetime.utcnow()
#         db.session.commit()
        
#         # Log activity
#         from activity_routes import log_activity
#         log_activity(
#             user_id=current_user.id,
#             user_name=current_user.full_name,
#             action='update',
#             resource_type='blog',
#             resource_id=post.id,
#             description=f'Updated blog post: {post.title}'
#         )
        
#         return jsonify({'message': 'Blog post updated'}), 200
        
#     except Exception as e:
#         db.session.rollback()
#         print(f"Error updating blog post: {str(e)}")
#         return jsonify({'error': str(e)}), 500







# ========== ADMIN BLOG ROUTES ==========

@app.route('/api/admin/blog', methods=['GET'])
@login_required

def admin_get_blog_posts():
    """Get all blog posts for admin panel (with author info)"""
    try:
        # Super admin sees all, regular admin sees only their own
        if current_user.role == 'super_admin':
            posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
        else:
            posts = BlogPost.query.filter_by(author_id=current_user.id).order_by(BlogPost.created_at.desc()).all()
        
        return jsonify([{
            'id': p.id,
            'title': p.title,
            'slug': p.slug,
            'excerpt': p.excerpt,
            'content': p.content,
            'featured_image': p.featured_image,
            'views': p.views,
            'status': p.status,
            'created_at': p.created_at.isoformat() if p.created_at else None,
            'updated_at': p.updated_at.isoformat() if p.updated_at else None,
            'author': p.author.full_name if p.author else 'Admin',
            'author_id': p.author_id,
            'can_edit': current_user.role == 'super_admin' or p.author_id == current_user.id
        } for p in posts]), 200
    except Exception as e:
        print(f"Error in get_admin_blog_posts: {e}")
        return jsonify([]), 200


@app.route('/api/admin/blog', methods=['POST'])
@login_required

def admin_create_blog_post():
    """Create a new blog post"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        if not data.get('slug'):
            return jsonify({'error': 'Slug is required'}), 400
        if not data.get('content'):
            return jsonify({'error': 'Content is required'}), 400
        
        # Check if slug already exists
        existing = BlogPost.query.filter_by(slug=data['slug']).first()
        if existing:
            return jsonify({'error': 'Slug already exists. Please use a different slug.'}), 400
        
        post = BlogPost(
            title=data['title'],
            slug=data['slug'],
            excerpt=data.get('excerpt', ''),
            content=data['content'],
            featured_image=data.get('featured_image', ''),
            status=data.get('status', 'draft'),  # Default to draft
            author_id=current_user.id  # Set author to current user
        )
        
        db.session.add(post)
        db.session.commit()
        
        # Log activity
        from activity_routes import log_activity
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='create',
            resource_type='blog',
            resource_id=post.id,
            description=f'Created blog post: {post.title}'
        )
        
        return jsonify({'message': 'Blog post created', 'id': post.id}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating blog post: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/blog/<int:id>', methods=['PUT'])
@login_required

def admin_update_blog_post(id):
    """Update an existing blog post (owner or super admin only)"""
    try:
        post = BlogPost.query.get_or_404(id)
        
        # Check permission: only author or super admin can edit
        if current_user.role != 'super_admin' and post.author_id != current_user.id:
            return jsonify({'error': 'You can only edit your own blog posts'}), 403
        
        data = request.json
        
        # Update allowed fields
        allowed_fields = ['title', 'slug', 'excerpt', 'content', 'featured_image', 'status']
        
        for key, value in data.items():
            if key in allowed_fields and hasattr(post, key):
                setattr(post, key, value)
        
        post.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log activity
        from activity_routes import log_activity
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='update',
            resource_type='blog',
            resource_id=post.id,
            description=f'Updated blog post: {post.title}'
        )
        
        return jsonify({'message': 'Blog post updated'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating blog post: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/blog/<int:id>', methods=['DELETE'])
@login_required

def admin_delete_blog_post(id):
    """Delete a blog post (owner or super admin only)"""
    try:
        post = BlogPost.query.get_or_404(id)
        
        # Check permission: only author or super admin can delete
        if current_user.role != 'super_admin' and post.author_id != current_user.id:
            return jsonify({'error': 'You can only delete your own blog posts'}), 403
        
        post_title = post.title
        db.session.delete(post)
        db.session.commit()
        
        # Log activity
        from activity_routes import log_activity
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='delete',
            resource_type='blog',
            resource_id=id,
            description=f'Deleted blog post: {post_title}'
        )
        
        return jsonify({'message': 'Blog post deleted'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting blog post: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/blog/<int:id>/status', methods=['PUT'])
@login_required

def update_blog_status(id):
    """Update only the status of a blog post (owner or super admin only)"""
    try:
        post = BlogPost.query.get_or_404(id)
        
        # Check permission
        if current_user.role != 'super_admin' and post.author_id != current_user.id:
            return jsonify({'error': 'You can only modify your own blog posts'}), 403
        
        data = request.json
        new_status = data.get('status')
        
        if new_status not in ['published', 'draft']:
            return jsonify({'error': 'Invalid status'}), 400
        
        post.status = new_status
        post.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': f'Blog post {new_status}'}), 200
        
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

# In backend/app.py
@app.errorhandler(404)
def not_found(error):
    from flask import request, jsonify
    if request.path.startswith('/api/'):
        return jsonify({
            "error": "Route Not Found",
            "message": f"Flask could not find an API route matching: {request.path}"
        }), 404
    
    # ... your fallback code for index.html ...
    return send_from_directory('../dist', 'index.html')

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    print(f"Server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


# Add at the bottom of app.py, before if __name__ == '__main__'
import traceback

@app.errorhandler(500)
def internal_error(error):
    print("=" * 50)
    print("500 ERROR DETAILS:")
    traceback.print_exc()
    print("=" * 50)
    return jsonify({'error': 'Internal server error', 'details': str(error)}), 500

# Handle favicon requests
@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return empty response with No Content status




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