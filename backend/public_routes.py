from flask import Blueprint, request, jsonify, current_app
from models import db, Product, BlogPost, Job, Outlet, Testimonial, Statistic, NewsletterSubscriber, TourPackage, TourAvailability, TourBooking, ContactMessage
from datetime import datetime
import re
import os
from email_service import EmailService
from models import db, Job, JobCategory, JobApplication, User

import secrets
from werkzeug.utils import secure_filename


public_bp = Blueprint('public', __name__, url_prefix='/api')
email_service = EmailService()
# ============================================================
# PRODUCTS
# ============================================================

@public_bp.route('/products', methods=['GET'])
def get_products():
    """Get products with pagination, filtering, and search"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        category = request.args.get('category', None)
        featured_only = request.args.get('featured', False, type=bool)
        search = request.args.get('search', None)
        
        page = max(1, page)
        per_page = min(50, max(1, per_page))
        
        query = Product.query.filter_by(is_active=True)
        
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
        
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': [{
                'id': p.id,
                'name': p.name,
                'slug': p.slug,
                'category': p.category,
                'description': p.description[:200] + '...' if len(p.description) > 200 else p.description,
                'benefits': p.benefits,
                'packaging_sizes': p.packaging_sizes,
                'nutritional_info': p.nutritional_info,
                'ingredients': p.ingredients,
                'image_url': p.image_url,
                'featured': p.featured,
                'qr_code_url': p.qr_code_url,
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
        return jsonify({'error': 'Failed to fetch products'}), 500

@public_bp.route('/products/featured', methods=['GET'])
def get_featured_products():
    """Get featured products"""
    try:
        limit = request.args.get('limit', 6, type=int)
        limit = min(12, max(1, limit))
        
        products = Product.query.filter_by(featured=True, is_active=True).limit(limit).all()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'category': p.category,
            'description': p.description[:120] + '...' if len(p.description) > 120 else p.description,
            'image_url': p.image_url,
            'featured': p.featured,
            'packaging_sizes': p.packaging_sizes,
            'qr_code_url': p.qr_code_url
        } for p in products])
    except Exception as e:
        return jsonify([]), 200

@public_bp.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    """Get single product by ID"""
    try:
        product = Product.query.get_or_404(id)
        return jsonify({
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'category': product.category,
            'description': product.description,
            'benefits': product.benefits,
            'packaging_sizes': product.packaging_sizes,
            'nutritional_info': product.nutritional_info,
            'ingredients': product.ingredients,
            'image_url': product.image_url,
            'featured': product.featured,
            'qr_code_url': product.qr_code_url
        })
    except Exception as e:
        return jsonify({'error': 'Product not found'}), 404

@public_bp.route('/products/slug/<slug>', methods=['GET'])
def get_product_by_slug(slug):
    """Get single product by slug"""
    try:
        product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
        return jsonify({
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'category': product.category,
            'description': product.description,
            'benefits': product.benefits,
            'packaging_sizes': product.packaging_sizes,
            'nutritional_info': product.nutritional_info,
            'ingredients': product.ingredients,
            'image_url': product.image_url,
            'featured': product.featured,
            'qr_code_url': product.qr_code_url
        })
    except Exception as e:
        return jsonify({'error': 'Product not found'}), 404

@public_bp.route('/products/categories', methods=['GET'])
def get_product_categories():
    """Get all unique product categories"""
    try:
        categories = db.session.query(Product.category).distinct().all()
        categories = [c[0] for c in categories if c[0]]
        return jsonify(['All'] + categories)
    except Exception as e:
        return jsonify(['All', 'Fresh Milk', 'Yoghurt', 'Lala', 'Ghee']), 200

# ============================================================
# BLOG
# ============================================================

@public_bp.route('/blog', methods=['GET'])
def get_blog_posts():
    """Get blog posts with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 6, type=int)
        
        page = max(1, page)
        per_page = min(20, max(1, per_page))
        
        query = BlogPost.query.filter_by(status='published').order_by(BlogPost.created_at.desc())
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': [{
                'id': p.id,
                'title': p.title,
                'slug': p.slug,
                'excerpt': p.excerpt,
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
        return jsonify([]), 200

@public_bp.route('/blog/<slug>', methods=['GET'])
def get_blog_post(slug):
    """Get single blog post by slug"""
    try:
        post = BlogPost.query.filter_by(slug=slug, status='published').first_or_404()
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
        return jsonify({'error': 'Post not found'}), 404

# ============================================================
# JOBS
# ============================================================

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_activity(user_id, user_name, action, resource_type, resource_id, description):
    try:
        from models import ActivityLog
        log = ActivityLog(
            user_id=user_id,
            user_name=user_name,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()


@public_bp.route('/jobs', methods=['GET'])
def get_jobs():
    """Get jobs with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category')
        location = request.args.get('location')
        type_filter = request.args.get('type')
        
        page = max(1, page)
        per_page = min(50, max(1, per_page))
        
        query = Job.query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(category_id=category)
        if location:
            query = query.filter(Job.location.ilike(f'%{location}%'))
        if type_filter:
            query = query.filter_by(type=type_filter)
        
        query = query.order_by(Job.created_at.desc())
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': [{
                'id': j.id,
                'title': j.title,
                'slug': j.slug,
                'category': j.category.name if j.category else None,
                'location': j.location,
                'type': j.type,
                'experience_level': j.experience_level,
                'salary_range': j.salary_range,
                'description': j.description[:150] + '...' if len(j.description) > 150 else j.description,
                'is_featured': j.is_featured,
                'views_count': j.views_count,
                'applications_count': j.applications_count,
                'application_deadline': j.application_deadline.isoformat() if j.application_deadline else None,
                'created_at': j.created_at.isoformat() if j.created_at else None
            } for j in paginated.items],
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
        return jsonify([]), 200

@public_bp.route('/jobs/<slug>', methods=['GET'])
def get_job(slug):
    """Get single job by slug"""
    try:
        job = Job.query.filter_by(slug=slug, is_active=True).first_or_404()
        job.views_count += 1
        db.session.commit()
        
        return jsonify({
            'id': job.id,
            'title': job.title,
            'slug': job.slug,
            'category': job.category.name if job.category else None,
            'location': job.location,
            'type': job.type,
            'experience_level': job.experience_level,
            'salary_range': job.salary_range,
            'description': job.description,
            'requirements': job.requirements,
            'responsibilities': job.responsibilities,
            'benefits': job.benefits,
            'application_deadline': job.application_deadline.isoformat() if job.application_deadline else None,
            'views_count': job.views_count,
            'created_at': job.created_at.isoformat() if job.created_at else None
        })
    except Exception as e:
        return jsonify({'error': 'Job not found'}), 404

@public_bp.route('/jobs/<int:job_id>/apply', methods=['POST'])
def apply_for_job(job_id):
    """Apply for a job"""
    try:
        from models import JobApplication
        from werkzeug.utils import secure_filename
        from app import app
        
        data = request.form
        files = request.files
        
        if not data.get('first_name') or not data.get('last_name') or not data.get('email') or not data.get('cover_letter'):
            return jsonify({'error': 'Please fill in all required fields'}), 400
        
        job = Job.query.get_or_404(job_id)
        
        # Handle CV upload
        cv_url = None
        if 'cv' in files and files['cv'].filename:
            file = files['cv']
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"cv_{timestamp}_{secure_filename(file.filename)}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'cvs', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            cv_url = f"/uploads/cvs/{filename}"
        
        application = JobApplication(
            job_id=job.id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone'),
            cover_letter=data['cover_letter'],
            cv_url=cv_url,
            portfolio_url=data.get('portfolio_url'),
            linkedin_url=data.get('linkedin_url'),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(application)
        db.session.commit()
        
        return jsonify({'message': 'Application submitted successfully', 'id': application.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@public_bp.route('/job-categories', methods=['GET'])
def get_job_categories():
    """Get all job categories"""
    try:
        from models import JobCategory
        categories = JobCategory.query.filter_by(is_active=True).all()
        return jsonify([{'id': c.id, 'name': c.name, 'slug': c.slug, 'icon': c.icon} for c in categories]), 200
    except Exception as e:
        return jsonify([]), 200

# ============================================================
# OUTLETS
# ============================================================

@public_bp.route('/outlets', methods=['GET'])
def get_outlets():
    """Get all active outlets"""
    try:
        category = request.args.get('category')
        
        query = Outlet.query.filter_by(is_active=True)
        if category and category != 'all':
            query = query.filter_by(category=category)
        
        outlets = query.order_by(Outlet.display_order, Outlet.name).all()
        
        return jsonify([{
            'id': o.id,
            'name': o.name,
            'category': o.category,
            'description': o.description,
            'address': o.address,
            'city': o.city,
            'latitude': o.latitude,
            'longitude': o.longitude,
            'phone': o.phone,
            'email': o.email,
            'working_hours': o.working_hours,
            'services': o.get_services_list()
        } for o in outlets]), 200
    except Exception as e:
        return jsonify([]), 200

@public_bp.route('/outlets/categories', methods=['GET'])
def get_outlet_categories():
    """Get all outlet categories with counts"""
    try:
        categories = [
            {'value': 'office_branch', 'label': '🏢 Office Branch', 'color': '#1e3a8a'},
            {'value': 'depot', 'label': '🚚 Depot / Distribution Center', 'color': '#f59e0b'},
            {'value': 'outlet', 'label': '🏪 Retail Outlet', 'color': '#10b981'}
        ]
        
        for cat in categories:
            cat['count'] = Outlet.query.filter_by(category=cat['value'], is_active=True).count()
        
        return jsonify(categories), 200
    except Exception as e:
        return jsonify([]), 200

# TESTIMONIALS

@public_bp.route('/testimonials', methods=['GET'])
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
        return jsonify([]), 200

# STATISTICS

@public_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get website statistics"""
    try:
        stats = Statistic.query.order_by(Statistic.order).all()
        return jsonify([{
            'id': s.id,
            'label': s.label,
            'value': s.value,
            'suffix': s.suffix
        } for s in stats])
    except Exception as e:
        return jsonify([]), 200

# TOURS 

@public_bp.route('/tour/packages', methods=['GET'])
def get_tour_packages():
    """Get all active tour packages"""
    try:
        packages = TourPackage.query.filter_by(is_active=True).all()
        return jsonify([p.to_dict() for p in packages]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@public_bp.route('/tour/availability', methods=['GET'])
def check_tour_availability():
    """Check if a date is available for booking"""
    try:
        package_id = request.args.get('package_id', type=int)
        date_str = request.args.get('date')
        
        if not package_id or not date_str:
            return jsonify({'error': 'Package ID and date are required'}), 400
        
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        availability = TourAvailability.query.filter_by(
            package_id=package_id,
            date=target_date
        ).first()
        
        if availability:
            return jsonify({
                'date': date_str,
                'is_blocked': availability.is_blocked,
                'block_reason': availability.block_reason,
                'is_available': not availability.is_blocked
            }), 200
        else:
            return jsonify({
                'date': date_str,
                'is_blocked': False,
                'block_reason': None,
                'is_available': True
            }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@public_bp.route('/tour/booking', methods=['POST'])
def create_tour_booking():
    """Public endpoint to create a tour booking"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['package_id', 'tour_date', 'people_count', 
                          'customer_name', 'customer_email', 'customer_phone']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        package = TourPackage.query.get(data['package_id'])
        if not package or not package.is_active:
            return jsonify({'error': 'Invalid or inactive package'}), 400
        
        people_count = int(data['people_count'])
        if people_count < package.min_people or people_count > package.max_people:
            return jsonify({'error': f'People count must be between {package.min_people} and {package.max_people}'}), 400
        
        tour_date = datetime.strptime(data['tour_date'], '%Y-%m-%d %H:%M:%S')
        
        # Check availability
        availability = TourAvailability.query.filter_by(
            package_id=package.id,
            date=tour_date.date()
        ).first()
        if availability and availability.is_blocked:
            return jsonify({'error': 'This date is not available'}), 400
        
        booking = TourBooking(
            package_id=package.id,
            tour_date=tour_date,
            people_count=people_count,
            customer_name=data['customer_name'].strip(),
            customer_email=data['customer_email'].strip(),
            customer_phone=data['customer_phone'].strip(),
            special_requirements=data.get('special_requirements'),
            group_name=data.get('group_name'),
            status='pending',
            payment_status='pending'
        )
        
        booking.generate_reference()
        price_data = package.get_price_for_people(people_count)
        
        booking.price_per_person = price_data['base_price']
        booking.subtotal = price_data['subtotal']
        booking.discount_applied = price_data['discount_amount']
        booking.total_amount = price_data['total']
        booking.commitment_amount = price_data['total'] * 0.30
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Booking submitted for approval',
            'booking': booking.to_dict(include_package=True),
            'price_breakdown': price_data
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# CONTACT

@public_bp.route('/contact', methods=['POST'])
def submit_contact():
    """Submit a contact message"""
    try:
        data = request.json
        
        if not data.get('name') or not data.get('email') or not data.get('message'):
            return jsonify({'error': 'Name, email, and message are required'}), 400
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        contact = ContactMessage(
            name=data['name'],
            email=data['email'],
            subject=data.get('subject', 'General Inquiry'),
            message=data['message'],
            status='unread'
        )
        db.session.add(contact)
        db.session.commit()
        
        return jsonify({'message': 'Message sent successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# NEWSLETTER

@public_bp.route('/newsletter/subscribe', methods=['POST'])
def subscribe_newsletter():
    """Subscribe to newsletter"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        email = data.get('email', '').lower().strip()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        existing = NewsletterSubscriber.query.filter_by(email=email).first()
        if existing:
            return jsonify({'message': 'Email already subscribed'}), 200
        
        subscriber = NewsletterSubscriber(
            name=name,
            email=email,
            subscribed_at=datetime.utcnow(),
            is_active=True
        )
        db.session.add(subscriber)
        db.session.commit()
        
        return jsonify({'message': 'Subscribed successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



@public_bp.route('/newsletter/unsubscribe', methods=['POST'])
def unsubscribe():
    """Public endpoint to unsubscribe"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        subscriber = NewsletterSubscriber.query.filter_by(email=email).first()
        
        if subscriber:
            subscriber.is_active = False
            db.session.commit()
            return jsonify({'message': 'Unsubscribed successfully'}), 200
        
        return jsonify({'message': 'Email not found'}), 404
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# REFERRAL REDIRECT

@public_bp.route('/r/<code>', methods=['GET'])
def referral_redirect(code):
    """Redirect for referral links"""
    try:
        from models import ReferralLink
        
        link = ReferralLink.query.filter_by(link_code=code, is_active=True).first()
        if not link:
            return jsonify({'error': 'Invalid referral link'}), 404
        
        link.increment_click(
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            referrer=request.referrer
        )
        
        if link.destination_url:
            return redirect(link.destination_url)
        else:
            return redirect('/')
    except Exception as e:
        return redirect('/')