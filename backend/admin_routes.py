from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from models import db, Product, BlogPost, Job, Outlet, ContactMessage, NewsletterSubscriber, User, Role, UserPermission, ActivityLog, DashboardComponent

from models import (
    db, Product, BlogPost, Job, Outlet, ContactMessage, 
    NewsletterSubscriber, User, Role, UserPermission, ActivityLog, 
    DashboardComponent, TourPackage, TourBooking, TourAvailability, 
    TourPayment, TourInvoice, ReferralLink, ReferralClick, RoleComponent,
    JobCategory, JobApplication)
from permission_service import require_permission, has_permission
from services.qr_code_service import QRCodeService
from services.component_service import ComponentService
from services.activity_logger import log_activity
from datetime import datetime
import os
import json
import re
import secrets
import string
from email_service import email_service
from permission_service import get_user_permissions
from datetime import datetime, timedelta



admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def user_has_component(component_key):
    """Check if current user has access to a component"""
    return ComponentService.user_can_access_component(component_key)

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ============================================================
# DASHBOARD CONFIG
# ============================================================

@admin_bp.route('/dashboard/config', methods=['GET'])
@login_required
def get_dashboard_config():
    """Get dashboard configuration for current user"""
    try:
        components = ComponentService.get_user_components()
        
        # ✅ Debug: Log component count
        
        return jsonify({
            'components': [c.to_dict() for c in components],
            'role': {
                'id': current_user.role_id,
                'name': current_user.role,
                'display_name': current_user.role.capitalize() if current_user.role else 'User'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# DEBUG PERMISSIONS
# ============================================================

@admin_bp.route('/debug/permissions', methods=['GET'])
@login_required
def debug_permissions():
    """Get current user's permissions for frontend debugging"""
    try:
        resources = ['products', 'blog', 'jobs', 'outlets', 'users', 'partners', 'referrals', 
                     'statistics', 'contacts', 'newsletter', 'tours', 'bookings', 'tour_settings',
                     'roles', 'permissions', 'components', 'profile', 'activities']
        actions = ['create', 'read', 'update', 'delete', 'approve', 'reject']
        
        permissions = {}
        for resource in resources:
            permissions[resource] = {}
            for action in actions:
                permissions[resource][action] = has_permission(current_user, resource, action)
        
        components = ComponentService.get_user_components()
        
        return jsonify({
            'user_id': current_user.id,
            'email': current_user.email,
            'full_name': current_user.full_name,
            'role': current_user.role,
            'is_super_admin': current_user.is_super_admin(),
            'permissions': permissions,
            'components': [c.to_dict() for c in components]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# OVERVIEW DASHBOARD

@admin_bp.route('/dashboard/overview', methods=['GET'])
@login_required
def get_dashboard_overview():
    """Get overview statistics for dashboard"""
    try:
        if not user_has_component('overview'):
            return jsonify({'error': 'Access denied'}), 403
        
        stats = {
            'total_products': Product.query.filter_by(is_active=True).count(),
            'total_jobs': Job.query.filter_by(is_active=True).count(),
            'total_tours': TourPackage.query.filter_by(is_active=True).count(),
            'total_bookings': TourBooking.query.count(),
            'total_partners': User.query.filter_by(role='partner').count(),
            'total_outlets': Outlet.query.filter_by(is_active=True).count(),
            'featured_products': [p.to_dict() for p in Product.query.filter_by(featured=True, is_active=True).limit(5).all()],
            'active_jobs': [{'id': j.id, 'title': j.title, 'location': j.location, 'created_at': j.created_at.isoformat() if j.created_at else None} for j in Job.query.filter_by(is_active=True).limit(5).all()],
            'upcoming_tours': [{'id': b.id, 'reference': b.reference, 'customer_name': b.customer_name, 'tour_date': b.tour_date.isoformat() if b.tour_date else None, 'status': b.status} for b in TourBooking.query.filter(TourBooking.tour_date >= datetime.utcnow(), TourBooking.status.in_(['confirmed', 'commitment_pending', 'cleared'])).limit(5).all()],
            'recent_bookings': [{'id': b.id, 'reference': b.reference, 'customer_name': b.customer_name, 'tour_date': b.tour_date.isoformat() if b.tour_date else None, 'status': b.status, 'created_at': b.created_at.isoformat() if b.created_at else None} for b in TourBooking.query.order_by(TourBooking.created_at.desc()).limit(5).all()],
            'recent_activities': [a.to_dict() for a in ActivityLog.query.filter_by(user_id=current_user.id).order_by(ActivityLog.created_at.desc()).limit(10).all()]
        }
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# PRODUCTS

@admin_bp.route('/products', methods=['GET'])
@login_required
def get_products():
    """Get all products for admin"""
    try:
        if not user_has_component('products'):
            return jsonify({'error': 'Access denied'}), 403
        products = Product.query.all()
        return jsonify([p.to_dict() for p in products]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/products', methods=['POST'])
@login_required
@require_permission('products', 'create')
def create_product():
    """Create a new product"""
    try:
        if not user_has_component('products'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.json
        slug = Product.generate_slug(data['name'])
        
        product = Product(
            name=data['name'],
            slug=slug,
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
        
        from services.qr_code_service import QRCodeService
        qr_service = QRCodeService()
        qr_service.regenerate_product_qr(product)
        db.session.commit()
        
        return jsonify({'message': 'Product created', 'id': product.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/products/<int:id>', methods=['PUT'])
@login_required
@require_permission('products', 'update')
def update_product(id):
    """Update a product"""
    try:
        if not user_has_component('products'):
            return jsonify({'error': 'Access denied'}), 403
        
        product = Product.query.get_or_404(id)
        data = request.json
        
        for key, value in data.items():
            if hasattr(product, key) and key not in ['id', 'created_at', 'updated_at', 'slug']:
                setattr(product, key, value)
        
        product.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Product updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/products/<int:id>', methods=['DELETE'])
@login_required
@require_permission('products', 'delete')
def delete_product(id):
    """Delete a product"""
    try:
        if not user_has_component('products'):
            return jsonify({'error': 'Access denied'}), 403
        
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/products/<int:id>/regenerate-qr', methods=['POST'])
@login_required
def regenerate_product_qr(id):
    """Regenerate QR code for a product"""
    try:
        if not user_has_component('products'):
            return jsonify({'error': 'Access denied'}), 403
        
        product = Product.query.get_or_404(id)
        qr_service = QRCodeService()
        qr_url = qr_service.regenerate_product_qr(product)
        db.session.commit()
        
        return jsonify({
            'message': 'QR code regenerated successfully',
            'qr_code_url': qr_url
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============================================================
# BLOG
# ============================================================

@admin_bp.route('/blog', methods=['GET'])
@login_required
def get_blog_posts():
    """Get all blog posts for admin"""
    try:
        if not user_has_component('blog'):
            return jsonify({'error': 'Access denied'}), 403
        
        posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
        return jsonify([{
            'id': p.id,
            'title': p.title,
            'slug': p.slug,
            'excerpt': p.excerpt,
            'content': p.content,
            'featured_image': p.featured_image,
            'views': p.views,
            'status': p.status,
            'author': p.author.full_name if p.author else 'Admin',
            'author_id': p.author_id,
            'created_at': p.created_at.isoformat() if p.created_at else None,
            'updated_at': p.updated_at.isoformat() if p.updated_at else None
        } for p in posts]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/blog', methods=['POST'])
@login_required
@require_permission('blog', 'create')
def create_blog_post():
    """Create a new blog post"""
    try:
        if not user_has_component('blog'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.json
        
        if not data.get('title') or not data.get('slug') or not data.get('content'):
            return jsonify({'error': 'Title, slug, and content are required'}), 400
        
        post = BlogPost(
            title=data['title'],
            slug=data['slug'],
            excerpt=data.get('excerpt', ''),
            content=data['content'],
            featured_image=data.get('featured_image', ''),
            status=data.get('status', 'draft'),
            author_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        return jsonify({'message': 'Blog post created', 'id': post.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/blog/<int:id>', methods=['PUT'])
@login_required
@require_permission('blog', 'update')
def update_blog_post(id):
    """Update a blog post"""
    try:
        if not user_has_component('blog'):
            return jsonify({'error': 'Access denied'}), 403
        
        post = BlogPost.query.get_or_404(id)
        data = request.json
        
        allowed_fields = ['title', 'slug', 'excerpt', 'content', 'featured_image', 'status']
        for key, value in data.items():
            if key in allowed_fields:
                setattr(post, key, value)
        
        post.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Blog post updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/blog/<int:id>', methods=['DELETE'])
@login_required
@require_permission('blog', 'delete')
def delete_blog_post(id):
    """Delete a blog post"""
    try:
        if not user_has_component('blog'):
            return jsonify({'error': 'Access denied'}), 403
        
        post = BlogPost.query.get_or_404(id)
        db.session.delete(post)
        db.session.commit()
        return jsonify({'message': 'Blog post deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/blog/<int:id>/status', methods=['PUT'])
@login_required
@require_permission('blog', 'update')
def update_blog_status(id):
    """Update blog post status"""
    try:
        if not user_has_component('blog'):
            return jsonify({'error': 'Access denied'}), 403
        
        post = BlogPost.query.get_or_404(id)
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



# ============================================================
# JOBS MANAGEMENT
# ============================================================

@admin_bp.route('/jobs', methods=['GET'])
@login_required
def get_jobs():
    """Get all jobs for admin"""
    try:
        if not user_has_component('jobs'):
            return jsonify({'error': 'Access denied'}), 403
        
        jobs = Job.query.order_by(Job.created_at.desc()).all()
        
        return jsonify([{
            'id': j.id,
            'title': j.title,
            'slug': j.slug,
            'category_id': j.category_id,
            'category': j.category.name if j.category else None,
            'location': j.location,
            'type': j.type,
            'experience_level': j.experience_level,
            'salary_range': j.salary_range,
            'description': j.description,
            'requirements': j.requirements,
            'responsibilities': j.responsibilities,
            'benefits': j.benefits,
            'application_deadline': j.application_deadline.isoformat() if j.application_deadline else None,
            'is_active': j.is_active,
            'is_featured': j.is_featured,
            'views_count': j.views_count,
            'applications_count': j.applications_count,
            'created_at': j.created_at.isoformat() if j.created_at else None,
            'updated_at': j.updated_at.isoformat() if j.updated_at else None
        } for j in jobs]), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/jobs', methods=['POST'])
@login_required
@require_permission('jobs', 'create')
def create_job():
    """Create a new job"""
    try:
        if not user_has_component('jobs'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.json
        
        # Validate required fields
        required_fields = ['title', 'description', 'requirements']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Generate slug
        slug = data.get('slug')
        if not slug:
            slug = data['title'].lower().replace(' ', '-')
            # Ensure uniqueness
            counter = 1
            while Job.query.filter_by(slug=slug).first():
                slug = f"{data['title'].lower().replace(' ', '-')}-{counter}"
                counter += 1
        
        job = Job(
            title=data['title'],
            slug=slug,
            category_id=data.get('category_id'),
            location=data.get('location'),
            type=data.get('type'),
            experience_level=data.get('experience_level'),
            salary_range=data.get('salary_range'),
            description=data['description'],
            requirements=data['requirements'],
            responsibilities=data.get('responsibilities'),
            benefits=data.get('benefits'),
            application_deadline=datetime.fromisoformat(data['application_deadline']) if data.get('application_deadline') else None,
            is_active=data.get('is_active', True),
            is_featured=data.get('is_featured', False),
            created_by=current_user.id
        )
        db.session.add(job)
        db.session.commit()
        
        return jsonify({'message': 'Job created', 'id': job.id, 'job': job.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/jobs/<int:id>', methods=['PUT'])
@login_required
@require_permission('jobs', 'update')
def update_job(id):
    """Update a job"""
    try:
        if not user_has_component('jobs'):
            return jsonify({'error': 'Access denied'}), 403
        
        job = Job.query.get_or_404(id)
        data = request.json
        
        updatable_fields = ['title', 'slug', 'category_id', 'location', 'type', 
                           'experience_level', 'salary_range', 'description', 
                           'requirements', 'responsibilities', 'benefits',
                           'application_deadline', 'is_active', 'is_featured']
        
        for field in updatable_fields:
            if field in data:
                if field == 'application_deadline' and data[field]:
                    value = datetime.fromisoformat(data[field])
                else:
                    value = data[field]
                setattr(job, field, value)
        
        job.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Job updated', 'job': job.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/jobs/<int:id>', methods=['DELETE'])
@login_required
@require_permission('jobs', 'delete')
def delete_job(id):
    """Delete a job"""
    try:
        if not user_has_component('jobs'):
            return jsonify({'error': 'Access denied'}), 403
        
        job = Job.query.get_or_404(id)
        
        # Delete associated applications first
        for app in job.applications:
            db.session.delete(app)
        
        db.session.delete(job)
        db.session.commit()
        
        return jsonify({'message': 'Job deleted'}), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500






# ============================================================
# JOB CATEGORIES
# ============================================================

@admin_bp.route('/job-categories', methods=['GET'])
@login_required
def get_job_categories():
    """Get all job categories for admin"""
    try:
        if not user_has_component('jobs'):
            return jsonify({'error': 'Access denied'}), 403
        
        
        categories = JobCategory.query.order_by(JobCategory.name).all()
      
        
        return jsonify([c.to_dict() for c in categories]), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/job-categories', methods=['POST'])
@login_required
@require_permission('jobs', 'create')
def create_job_category():
    """Create a new job category"""
    try:
        if not user_has_component('jobs'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.json
        
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        
        # Generate slug
        import re
        slug = re.sub(r'[^a-z0-9-]', '-', data['name'].lower().replace(' ', '-'))
        slug = re.sub(r'-+', '-', slug).strip('-')
        
        # Ensure uniqueness
        counter = 1
        original_slug = slug
        while JobCategory.query.filter_by(slug=slug).first():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        category = JobCategory(
            name=data['name'],
            slug=slug,
            description=data.get('description'),
            icon=data.get('icon'),
            is_active=data.get('is_active', True)
        )
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Category created',
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/job-categories/<int:category_id>', methods=['PUT'])
@login_required
@require_permission('jobs', 'update')
def update_job_category(category_id):
    """Update a job category"""
    try:
        if not user_has_component('jobs'):
            return jsonify({'error': 'Access denied'}), 403
        
        category = JobCategory.query.get_or_404(category_id)
        data = request.json
        
        if 'name' in data and data['name'] != category.name:
            category.name = data['name']
            import re
            slug = re.sub(r'[^a-z0-9-]', '-', data['name'].lower().replace(' ', '-'))
            slug = re.sub(r'-+', '-', slug).strip('-')
            # Ensure uniqueness
            counter = 1
            original_slug = slug
            while JobCategory.query.filter_by(slug=slug).first() and slug != category.slug:
                slug = f"{original_slug}-{counter}"
                counter += 1
            category.slug = slug
        
        if 'description' in data:
            category.description = data['description']
        if 'icon' in data:
            category.icon = data['icon']
        if 'is_active' in data:
            category.is_active = data['is_active']
        
        category.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Category updated',
            'category': category.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/job-categories/<int:category_id>', methods=['DELETE'])
@login_required
@require_permission('jobs', 'delete')
def delete_job_category(category_id):
    """Delete a job category"""
    try:
        if not user_has_component('jobs'):
            return jsonify({'error': 'Access denied'}), 403
        
        category = JobCategory.query.get_or_404(category_id)
        
        # Check if category has jobs
        job_count = Job.query.filter_by(category_id=category_id).count()
        if job_count > 0:
            return jsonify({'error': f'Cannot delete category with {job_count} existing jobs'}), 400
        
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Category deleted'}), 200
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



# ============================================================
# JOB APPLICATIONS
# ============================================================

@admin_bp.route('/applications', methods=['GET'])
@login_required
def get_job_applications():
    """Get all job applications for admin"""
    try:
        if not user_has_component('jobs'):
            return jsonify({'error': 'Access denied'}), 403
        
        status = request.args.get('status')
        job_id = request.args.get('job_id', type=int)
        
        query = JobApplication.query
        
        if status:
            query = query.filter_by(status=status)
        if job_id:
            query = query.filter_by(job_id=job_id)
        
        applications = query.order_by(JobApplication.applied_at.desc()).all()
        
        return jsonify([{
            'id': a.id,
            'job_id': a.job_id,
            'job_title': a.job.title if a.job else None,
            'first_name': a.first_name,
            'last_name': a.last_name,
            'full_name': a.get_full_name(),
            'email': a.email,
            'phone': a.phone,
            'cover_letter': a.cover_letter,
            'cv_url': a.cv_url,
            'portfolio_url': a.portfolio_url,
            'linkedin_url': a.linkedin_url,
            'status': a.status,
            'admin_notes': a.admin_notes,
            'rating': a.rating,
            'applied_at': a.applied_at.isoformat() if a.applied_at else None
        } for a in applications]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/applications/<int:application_id>', methods=['GET'])
@login_required
def get_job_application(application_id):
    """Get a single job application"""
    try:
        if not user_has_component('jobs'):
            return jsonify({'error': 'Access denied'}), 403
        
        application = JobApplication.query.get_or_404(application_id)
        return jsonify({
            'id': application.id,
            'job_id': application.job_id,
            'job_title': application.job.title if application.job else None,
            'first_name': application.first_name,
            'last_name': application.last_name,
            'full_name': application.get_full_name(),
            'email': application.email,
            'phone': application.phone,
            'cover_letter': application.cover_letter,
            'cv_url': application.cv_url,
            'portfolio_url': application.portfolio_url,
            'linkedin_url': application.linkedin_url,
            'status': application.status,
            'admin_notes': application.admin_notes,
            'rating': application.rating,
            'applied_at': application.applied_at.isoformat() if application.applied_at else None
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/applications/<int:application_id>/status', methods=['PUT'])
@login_required
@require_permission('jobs', 'update')
def update_job_application_status(application_id):
    """Update job application status"""
    try:
        if not user_has_component('jobs'):
            return jsonify({'error': 'Access denied'}), 403
        
        application = JobApplication.query.get_or_404(application_id)
        data = request.json
        new_status = data.get('status')
        
        valid_statuses = ['pending', 'reviewed', 'shortlisted', 'rejected', 'hired']
        if new_status not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400
        
        application.status = new_status
        application.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': f'Application {new_status}'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/applications/<int:application_id>/reply', methods=['POST'])
@login_required
@require_permission('jobs', 'update')
def reply_to_job_application(application_id):
    """Reply to a job application"""
    try:
        if not user_has_component('jobs'):
            return jsonify({'error': 'Access denied'}), 403
        
        application = JobApplication.query.get_or_404(application_id)
        data = request.json
        reply_message = data.get('reply')
        
        if not reply_message:
            return jsonify({'error': 'Reply message is required'}), 400
        
        application.admin_reply = reply_message
        application.replied_at = datetime.utcnow()
        application.replied_by = current_user.id
        db.session.commit()
        
        return jsonify({'message': 'Reply sent'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500





# ============================================================
# OUTLETS
# ============================================================

@admin_bp.route('/outlets', methods=['GET'])
@login_required
def get_outlets():
    """Get all outlets for admin"""
    try:
        if not user_has_component('outlets'):
            return jsonify({'error': 'Access denied'}), 403
        
        outlets = Outlet.query.order_by(Outlet.display_order, Outlet.name).all()
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
            'services': o.get_services_list(),
            'is_active': o.is_active,
            'display_order': o.display_order,
            'created_at': o.created_at.isoformat() if o.created_at else None
        } for o in outlets]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/outlets', methods=['POST'])
@login_required
@require_permission('outlets', 'create')
def create_outlet():
    """Create a new outlet"""
    try:
        if not user_has_component('outlets'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.json
        
        required_fields = ['name', 'category', 'address', 'latitude', 'longitude']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        outlet = Outlet(
            name=data['name'],
            category=data['category'],
            description=data.get('description', ''),
            address=data['address'],
            city=data.get('city', ''),
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            working_hours=data.get('working_hours', ''),
            is_active=data.get('is_active', True),
            display_order=data.get('display_order', 0)
        )
        
        if data.get('services'):
            outlet.set_services_list(data['services'])
        
        db.session.add(outlet)
        db.session.commit()
        return jsonify({'message': 'Outlet created', 'id': outlet.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/outlets/<int:id>', methods=['PUT'])
@login_required
@require_permission('outlets', 'update')
def update_outlet(id):
    """Update an outlet"""
    try:
        if not user_has_component('outlets'):
            return jsonify({'error': 'Access denied'}), 403
        
        outlet = Outlet.query.get_or_404(id)
        data = request.json
        
        updatable_fields = ['name', 'category', 'description', 'address', 'city',
                           'latitude', 'longitude', 'phone', 'email', 'working_hours',
                           'is_active', 'display_order']
        
        for field in updatable_fields:
            if field in data:
                if field in ['latitude', 'longitude']:
                    setattr(outlet, field, float(data[field]))
                else:
                    setattr(outlet, field, data[field])
        
        if 'services' in data:
            outlet.set_services_list(data['services'])
        
        outlet.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Outlet updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/outlets/<int:id>', methods=['DELETE'])
@login_required
@require_permission('outlets', 'delete')
def delete_outlet(id):
    """Delete an outlet"""
    try:
        if not user_has_component('outlets'):
            return jsonify({'error': 'Access denied'}), 403
        
        outlet = Outlet.query.get_or_404(id)
        db.session.delete(outlet)
        db.session.commit()
        return jsonify({'message': 'Outlet deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============================================================
# CONTACT MESSAGES
# ============================================================

@admin_bp.route('/contacts', methods=['GET'])
@login_required
def get_contacts():
    """Get all contact messages"""
    try:
        if not user_has_component('contacts'):
            return jsonify({'error': 'Access denied'}), 403
        
        contacts = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
        return jsonify([c.to_dict() for c in contacts]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/contacts/stats', methods=['GET'])
@login_required
def get_contact_stats():
    """Get contact message statistics"""
    try:
        if not user_has_component('contacts'):
            return jsonify({'error': 'Access denied'}), 403
        
        total = ContactMessage.query.count()
        unread = ContactMessage.query.filter_by(status='unread').count()
        read = ContactMessage.query.filter_by(status='read').count()
        replied = ContactMessage.query.filter_by(status='replied').count()
        archived = ContactMessage.query.filter_by(status='archived').count()
        
        return jsonify({
            'total': total,
            'unread': unread,
            'read': read,
            'replied': replied,
            'archived': archived
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/contacts/<int:id>', methods=['GET'])
@login_required
def get_contact(id):
    """Get a single contact message"""
    try:
        if not user_has_component('contacts'):
            return jsonify({'error': 'Access denied'}), 403
        
        contact = ContactMessage.query.get_or_404(id)
        return jsonify(contact.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/contacts/<int:id>/status', methods=['PUT'])
@login_required
@require_permission('contacts', 'update')
def update_contact_status(id):
    """Update contact message status"""
    try:
        if not user_has_component('contacts'):
            return jsonify({'error': 'Access denied'}), 403
        
        contact = ContactMessage.query.get_or_404(id)
        data = request.json
        new_status = data.get('status')
        
        if new_status not in ['unread', 'read', 'replied', 'archived']:
            return jsonify({'error': 'Invalid status'}), 400
        
        contact.status = new_status
        db.session.commit()
        return jsonify({'message': 'Contact status updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/contacts/<int:id>', methods=['DELETE'])
@login_required
@require_permission('contacts', 'delete')
def delete_contact(id):
    """Delete a contact message"""
    try:
        if not user_has_component('contacts'):
            return jsonify({'error': 'Access denied'}), 403
        
        contact = ContactMessage.query.get_or_404(id)
        db.session.delete(contact)
        db.session.commit()
        return jsonify({'message': 'Contact deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============================================================
# NEWSLETTER
# ============================================================

@admin_bp.route('/newsletter/subscribers', methods=['GET'])
@login_required
def get_newsletter_subscribers():
    """Get all newsletter subscribers"""
    try:
        if not user_has_component('newsletter'):
            return jsonify({'error': 'Access denied'}), 403
        
        subscribers = NewsletterSubscriber.query.order_by(NewsletterSubscriber.subscribed_at.desc()).all()
        return jsonify([{
            'id': s.id,
            'name': s.name,
            'email': s.email,
            'is_active': s.is_active,
            'subscribed_at': s.subscribed_at.isoformat() if s.subscribed_at else None
        } for s in subscribers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/newsletter/subscribers/stats', methods=['GET'])
@login_required
def get_subscriber_stats():
    """Get newsletter statistics"""
    try:
        if not user_has_component('newsletter'):
            return jsonify({'error': 'Access denied'}), 403
        
        total = NewsletterSubscriber.query.count()
        active = NewsletterSubscriber.query.filter_by(is_active=True).count()
        inactive = NewsletterSubscriber.query.filter_by(is_active=False).count()
        
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        new_last_30 = NewsletterSubscriber.query.filter(
            NewsletterSubscriber.subscribed_at >= thirty_days_ago
        ).count()
        
        return jsonify({
            'total': total,
            'active': active,
            'inactive': inactive,
            'new_last_30_days': new_last_30
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/newsletter/subscribers/<int:subscriber_id>', methods=['DELETE'])
@login_required
@require_permission('newsletter', 'delete')
def delete_subscriber(subscriber_id):
    """Delete a subscriber"""
    try:
        if not user_has_component('newsletter'):
            return jsonify({'error': 'Access denied'}), 403
        
        subscriber = NewsletterSubscriber.query.get_or_404(subscriber_id)
        db.session.delete(subscriber)
        db.session.commit()
        
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='delete',
            resource_type='newsletter',
            resource_id=subscriber_id,
            description=f'Deleted newsletter subscriber: {subscriber.email}'
        )
        
        return jsonify({'message': 'Subscriber deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/newsletter/subscribers/<int:subscriber_id>/toggle', methods=['PUT'])
@login_required
@require_permission('newsletter', 'update')
def toggle_subscriber_status(subscriber_id):
    """Toggle subscriber active status"""
    try:
        if not user_has_component('newsletter'):
            return jsonify({'error': 'Access denied'}), 403
        
        subscriber = NewsletterSubscriber.query.get_or_404(subscriber_id)
        subscriber.is_active = not subscriber.is_active
        db.session.commit()
        
        status = 'activated' if subscriber.is_active else 'deactivated'
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='toggle',
            resource_type='newsletter',
            resource_id=subscriber_id,
            description=f'{status} newsletter subscriber: {subscriber.email}'
        )
        
        return jsonify({'message': f'Subscriber {status}'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/newsletter/send', methods=['POST'])
@login_required
@require_permission('newsletter', 'create')
def send_newsletter():
    """Send newsletter to all active subscribers"""
    try:
        if not user_has_component('newsletter'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.json
        subject = data.get('subject', '').strip()
        content = data.get('content', '').strip()
        is_test = data.get('is_test', False)
        test_email = data.get('test_email', '')
        
        if not subject or not content:
            return jsonify({'error': 'Subject and content are required'}), 400
        
        if is_test and not test_email:
            return jsonify({'error': 'Test email address required'}), 400
        
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        
        if is_test:
            unsubscribe_token = secrets.token_urlsafe(32)
            html = build_newsletter_html(subject, content, test_email, unsubscribe_token, frontend_url)
            email_service._send_email(test_email, f"[TEST] {subject}", html)
            return jsonify({'message': 'Test email sent'}), 200
        
        subscribers = NewsletterSubscriber.query.filter_by(is_active=True).all()
        
        if not subscribers:
            return jsonify({'error': 'No active subscribers'}), 400
        
        sent_count = 0
        failed_count = 0
        
        for subscriber in subscribers:
            try:
                unsubscribe_token = secrets.token_urlsafe(32)
                html = build_newsletter_html(subject, content, subscriber.email, unsubscribe_token, frontend_url)
                
                if email_service._send_email(subscriber.email, subject, html):
                    sent_count += 1
                    subscriber.last_sent = datetime.utcnow()
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
        
        db.session.commit()
        
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='send_newsletter',
            resource_type='newsletter',
            resource_id=0,
            description=f'Sent newsletter "{subject}" to {sent_count} subscribers'
        )
        
        return jsonify({
            'message': f'Newsletter sent to {sent_count} subscribers',
            'sent': sent_count,
            'failed': failed_count
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def build_newsletter_html(subject, content, email, unsubscribe_token, frontend_url):
    """Build HTML for newsletter email"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{subject}</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 30px; text-align: center; }}
            .content {{ padding: 30px; background: #f9fafb; }}
            .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #ddd; }}
            .unsubscribe {{ color: #f59e0b; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Meru Dairy Newsletter</h2>
            </div>
            <div class="content">
                <h3>{subject}</h3>
                <div style="white-space: pre-wrap;">{content}</div>
            </div>
            <div class="footer">
                <p>Meru Central Dairy Co-operative Union Ltd</p>
                <p><a href="{frontend_url}/unsubscribe?email={email}&token={unsubscribe_token}" class="unsubscribe">Unsubscribe</a> from future emails</p>
            </div>
        </div>
    </body>
    </html>
    """

@admin_bp.route('/newsletter/export', methods=['GET'])
@login_required
def export_subscribers():
    """Export subscribers to CSV"""
    try:
        if not user_has_component('newsletter'):
            return jsonify({'error': 'Access denied'}), 403
        
        import csv
        from io import StringIO
        
        subscribers = NewsletterSubscriber.query.filter_by(is_active=True).order_by(NewsletterSubscriber.subscribed_at.desc()).all()
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Name', 'Email', 'Subscribed Date', 'Status'])
        
        for sub in subscribers:
            writer.writerow([
                sub.name or '',
                sub.email,
                sub.subscribed_at.strftime('%Y-%m-%d %H:%M:%S') if sub.subscribed_at else '',
                'Active' if sub.is_active else 'Inactive'
            ])
        
        return jsonify({
            'csv_content': output.getvalue(),
            'filename': f'newsletter_subscribers_{datetime.utcnow().strftime("%Y%m%d")}.csv'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# TOUR MANAGEMENT
# ============================================================

@admin_bp.route('/tour/bookings', methods=['GET'])
@login_required
def get_tour_bookings():
    """Get all tour bookings"""
    try:
        if not user_has_component('tours'):
            return jsonify({'error': 'Access denied'}), 403
        
        bookings = TourBooking.query.order_by(TourBooking.created_at.desc()).all()
        return jsonify({'bookings': [b.to_dict(include_package=True) for b in bookings]}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



@admin_bp.route('/tour/bookings/<int:id>', methods=['GET'])
@login_required
def get_tour_booking(id):
    """Get a single tour booking"""
    try:
        if not user_has_component('tours'):
            return jsonify({'error': 'Access denied'}), 403
        
        booking = TourBooking.query.get_or_404(id)
        return jsonify(booking.to_dict(include_package=True)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/tour/bookings/<int:id>/status', methods=['PUT'])
@login_required
@require_permission('bookings', 'update')
def update_booking_status(id):
    """Update booking status"""
    try:
        if not user_has_component('tours'):
            return jsonify({'error': 'Access denied'}), 403
        
        booking = TourBooking.query.get_or_404(id)
        data = request.json
        new_status = data.get('status')
        
        valid_statuses = ['pending', 'confirmed', 'rejected', 'completed', 'cancelled', 'commitment_pending', 'cleared']
        if new_status not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400
        
        booking.status = new_status
        booking.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': f'Booking {new_status}', 'booking': booking.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/tour/packages', methods=['GET'])
@login_required
def get_tour_packages():
    """Get all tour packages"""
    try:
        # Check if user has access
        if not user_has_component('tour-packages'):
            return jsonify({'error': 'Access denied'}), 403
        
        # Get all active packages
        packages = TourPackage.query.filter_by(is_active=True).all()
        
    
        
        # Return as dictionary
        return jsonify({
            'packages': [p.to_dict() for p in packages]
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



@admin_bp.route('/tour/packages', methods=['POST'])
@login_required
@require_permission('tour-packages', 'create')
def create_tour_package():
    """Create a tour package"""
    try:
        if not user_has_component('tour-packages'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.json
        
        required_fields = ['name', 'slug', 'description', 'base_price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        package = TourPackage(
            name=data['name'],
            slug=data['slug'],
            description=data['description'],
            short_description=data.get('short_description'),
            base_price=data['base_price'],
            min_people=data.get('min_people', 1),
            max_people=data.get('max_people', 300),
            commitment_percentage=data.get('commitment_percentage', 30.0),
            discount_tiers=data.get('discount_tiers', {
                '1-50': 0.05,
                '51-100': 0.10,
                '101-150': 0.15,
                '151-200': 0.20,
                '201+': 0.25
            }),
            duration_hours=data.get('duration_hours', 2),
            includes=data.get('includes', []),
            excludes=data.get('excludes', []),
            image_url=data.get('image_url'),
            gallery_images=data.get('gallery_images', []),
            is_active=data.get('is_active', True),
            is_featured=data.get('is_featured', False),
            created_by_id=current_user.id
        )
        
        db.session.add(package)
        db.session.commit()
        return jsonify({'message': 'Package created', 'package': package.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/tour/packages/<int:id>', methods=['PUT'])
@login_required
@require_permission('tour-packages', 'update')
def update_tour_package(id):
    """Update a tour package"""
    try:
        if not user_has_component('tour-packages'):
            return jsonify({'error': 'Access denied'}), 403
        
        package = TourPackage.query.get_or_404(id)
        data = request.json
        
        updatable_fields = ['name', 'slug', 'description', 'short_description', 'base_price',
                           'min_people', 'max_people', 'commitment_percentage', 'discount_tiers',
                           'duration_hours', 'includes', 'excludes', 'image_url', 'gallery_images',
                           'is_active', 'is_featured']
        
        for field in updatable_fields:
            if field in data:
                setattr(package, field, data[field])
        
        package.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Package updated', 'package': package.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/tour/packages/<int:id>', methods=['DELETE'])
@login_required
@require_permission('tour-packages', 'delete')
def delete_tour_package(id):
    """Delete a tour package"""
    try:
        if not user_has_component('tour-packages'):
            return jsonify({'error': 'Access denied'}), 403
        
        package = TourPackage.query.get_or_404(id)
        
        if package.bookings.count() > 0:
            return jsonify({'error': 'Cannot delete package with existing bookings'}), 400
        
        db.session.delete(package)
        db.session.commit()
        return jsonify({'message': 'Package deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500




@admin_bp.route('/tour/reports/summary', methods=['GET'])
@login_required
def get_tour_reports_summary():
    """Get tour reports summary with actual data"""
    try:
        if not user_has_component('tour-reports'):
            return jsonify({'error': 'Access denied'}), 403
        
        # Get date parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # ✅ Handle missing dates with defaults
        if not start_date_str or not end_date_str:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
        else:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
            except ValueError as e:
                return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
        
        # ✅ Ensure we have valid dates
        if start_date > end_date:
            return jsonify({'error': 'Start date must be before end date'}), 400
        
        # Query bookings within date range
        bookings = TourBooking.query.filter(
            TourBooking.created_at >= start_date,
            TourBooking.created_at < end_date
        ).all()
        
        # Calculate statistics from actual data
        total_bookings = len(bookings)
        total_revenue = sum(b.total_amount for b in bookings if b.status in ['completed', 'cleared'])
        total_visitors = sum(b.people_count for b in bookings) if bookings else 0
        
        # Status breakdown
        statuses = {
            'pending': len([b for b in bookings if b.status == 'pending']),
            'confirmed': len([b for b in bookings if b.status == 'confirmed']),
            'completed': len([b for b in bookings if b.status == 'completed']),
            'cancelled': len([b for b in bookings if b.status == 'cancelled']),
            'rejected': len([b for b in bookings if b.status == 'rejected']),
            'commitment_pending': len([b for b in bookings if b.status == 'commitment_pending']),
            'cleared': len([b for b in bookings if b.status == 'cleared']),
        }
        
        # Package popularity
        package_counts = {}
        package_revenue = {}
        for b in bookings:
            if b.package_id:
                package_counts[b.package_id] = package_counts.get(b.package_id, 0) + 1
                if b.status in ['completed', 'cleared']:
                    package_revenue[b.package_id] = package_revenue.get(b.package_id, 0) + b.total_amount
        
        popular_packages = []
        for pkg_id, count in sorted(package_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            pkg = TourPackage.query.get(pkg_id)
            if pkg:
                popular_packages.append({
                    'id': pkg.id,
                    'name': pkg.name,
                    'total_bookings': count,
                    'percentage': round((count / total_bookings * 100), 1) if total_bookings > 0 else 0,
                    'revenue': package_revenue.get(pkg_id, 0)
                })
        
        # Daily booking data for charts
        daily_data = {}
        for b in bookings:
            date_key = b.created_at.strftime('%Y-%m-%d')
            if date_key not in daily_data:
                daily_data[date_key] = {'bookings': 0, 'revenue': 0}
            daily_data[date_key]['bookings'] += 1
            if b.status in ['completed', 'cleared']:
                daily_data[date_key]['revenue'] += b.total_amount
        
        # Sort daily data
        sorted_dates = sorted(daily_data.keys())
        daily_bookings = [daily_data[d]['bookings'] for d in sorted_dates]
        daily_revenue = [daily_data[d]['revenue'] for d in sorted_dates]
        
        # Conversion rate
        conversion_rate = round((statuses['completed'] / total_bookings * 100), 1) if total_bookings > 0 else 0
        
        # Recent activity (last 10 bookings)
        recent_activity = []
        for b in bookings[:10]:
            recent_activity.append({
                'id': b.id,
                'type': b.status,
                'message': f'{b.status.title()} booking - {b.customer_name}',
                'created_at': b.created_at.isoformat() if b.created_at else None
            })
        
        return jsonify({
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
            'total_visitors': total_visitors,
            'conversion_rate': conversion_rate,
            'pending': statuses['pending'],
            'confirmed': statuses['confirmed'],
            'completed': statuses['completed'],
            'cancelled': statuses['cancelled'],
            'rejected': statuses['rejected'],
            'commitment_pending': statuses['commitment_pending'],
            'cleared': statuses['cleared'],
            'popular_packages': popular_packages,
            'recent_activity': recent_activity,
            'daily_bookings': daily_bookings,
            'daily_dates': sorted_dates,
            'daily_revenue': daily_revenue,
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ============================================================
# PARTNERS & REFERRALS
# ============================================================

@admin_bp.route('/partners', methods=['GET'])
@login_required
def get_partners():
    """Get all partners"""
    try:
        if not user_has_component('partners'):
            return jsonify({'error': 'Access denied'}), 403
        
        partners = User.query.filter_by(role='partner').all()
        return jsonify([{
            'id': p.id,
            'email': p.email,
            'full_name': p.full_name,
            'referral_code': p.referral_code,
            'total_clicks': p.total_clicks,
            'total_conversions': p.total_conversions,
            'is_active': p.is_active,
            'created_at': p.created_at.isoformat() if p.created_at else None
        } for p in partners]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/partners/<int:id>', methods=['PUT'])
@login_required
@require_permission('partners', 'update')
def update_partner(id):
    """Update a partner"""
    try:
        if not user_has_component('partners'):
            return jsonify({'error': 'Access denied'}), 403
        
        partner = User.query.get_or_404(id)
        data = request.json
        
        if 'full_name' in data:
            partner.full_name = data['full_name']
        if 'is_active' in data:
            partner.is_active = data['is_active']
        
        partner.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Partner updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/partners/links', methods=['GET'])
@login_required
def get_partner_links():
    """Get all referral links"""
    try:
        if not user_has_component('partner-links'):
            return jsonify({'error': 'Access denied'}), 403
        
        links = ReferralLink.query.order_by(ReferralLink.created_at.desc()).all()
        return jsonify([l.to_dict() for l in links]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500




# @admin_bp.route('/partners/links', methods=['POST'])
# @login_required
# @require_permission('partner-links', 'create')
# def create_partner_link():
#     """Create a referral link"""
#     try:
#         if not user_has_component('partner-links'):
#             return jsonify({'error': 'Access denied'}), 403
        
#         data = request.json
        
#         link = ReferralLink(
#             user_id=current_user.id,
#             name=data['name'],
#             destination_url=data.get('destination_url'),
#             campaign_name=data.get('campaign_name'),
#             is_active=data.get('is_active', True)
#         )
#         link.generate_code()
#         db.session.add(link)
#         db.session.commit()
#         return jsonify({'message': 'Link created', 'link': link.to_dict()}), 201
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500



@admin_bp.route('/partners/analytics', methods=['GET'])
@login_required
def get_partner_analytics():
    """Get referral analytics"""
    try:
        if not user_has_component('partner-analytics'):
            return jsonify({'error': 'Access denied'}), 403
        
        total_links = ReferralLink.query.count()
        total_clicks = db.session.query(db.func.sum(ReferralLink.total_clicks)).scalar() or 0
        total_conversions = db.session.query(db.func.sum(ReferralLink.conversions)).scalar() or 0
        
        return jsonify({
            'total_links': total_links,
            'total_clicks': total_clicks,
            'total_conversions': total_conversions,
            'conversion_rate': round((total_conversions / total_clicks * 100), 2) if total_clicks > 0 else 0
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# PROFILE
# ============================================================

@admin_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get current user profile"""
    try:
        if not user_has_component('profile'):
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify(current_user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update current user profile"""
    try:
        if not user_has_component('profile'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.json
        full_name = data.get('full_name')
        
        if full_name:
            current_user.full_name = full_name
            db.session.commit()
        
        return jsonify({'message': 'Profile updated', 'user': current_user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/change-password', methods=['PUT'])
@login_required
def change_password():
    """Change current user password"""
    try:
        if not user_has_component('profile'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.json
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        from auth_routes import validate_password
        valid, message = validate_password(new_password)
        if not valid:
            return jsonify({'error': message}), 400
        
        current_user.set_password(new_password)
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============================================================
# USERS
# ============================================================

@admin_bp.route('/users', methods=['GET'])
@login_required
def get_users():
    """Get all users"""
    try:
        if not user_has_component('users'):
            return jsonify({'error': 'Access denied'}), 403
        
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify([{
            'id': u.id,
            'email': u.email,
            'full_name': u.full_name,
            'role': u.role,
            'role_id': u.role_id,
            'is_active': u.is_active,
            'is_approved': u.is_approved,
            'email_verified': u.email_verified,
            'referral_code': u.referral_code,
            'total_clicks': u.total_clicks,
            'total_conversions': u.total_conversions,
            'created_at': u.created_at.isoformat() if u.created_at else None,
            'last_login': u.last_login.isoformat() if u.last_login else None
        } for u in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users', methods=['POST'])
@login_required
@require_permission('users', 'create')
def create_user():
    """Create a new user"""
    try:
        if not user_has_component('users'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.json
        email = data.get('email', '').lower().strip()
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'User already exists'}), 400
        
        role_name = data.get('role', 'partner')
        role_id = data.get('role_id')
        
        if role_id:
            role = Role.query.get(role_id)
            if role:
                role_name = role.name
        
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        
        user = User(
            email=email,
            full_name=data.get('full_name', '').strip(),
            role=role_name,
            role_id=role_id,
            is_active=data.get('is_active', True),
            is_approved=data.get('is_approved', True),
            email_verified=True,
            created_by_id=current_user.id
        )
        user.set_password(temp_password)
        db.session.add(user)
        db.session.commit()
        
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='create',
            resource_type='user',
            resource_id=user.id,
            description=f'Created user: {user.email}'
        )
        
        return jsonify({
            'message': 'User created',
            'user': user.to_dict(),
            'temporary_password': temp_password
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:id>', methods=['PUT'])
@login_required
@require_permission('users', 'update')
def update_user(id):
    """Update a user"""
    try:
        if not user_has_component('users'):
            return jsonify({'error': 'Access denied'}), 403
        
        user = User.query.get_or_404(id)
        data = request.json
        
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'role_id' in data:
            role = Role.query.get(data['role_id'])
            if role:
                user.role = role.name
                user.role_id = role.id
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'is_approved' in data:
            user.is_approved = data['is_approved']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'User updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:id>', methods=['DELETE'])
@login_required
@require_permission('users', 'delete')
def delete_user(id):
    """Delete a user"""
    try:
        if not user_has_component('users'):
            return jsonify({'error': 'Access denied'}), 403
        
        user = User.query.get_or_404(id)
        
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot delete yourself'}), 400
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============================================================
# ROLES
# ============================================================

@admin_bp.route('/roles', methods=['GET'])
@login_required
def get_roles():
    """Get all roles"""
    try:
        if not user_has_component('roles'):
            return jsonify({'error': 'Access denied'}), 403
        
        roles = Role.query.all()
        return jsonify([r.to_dict() for r in roles]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/roles', methods=['POST'])
@login_required
@require_permission('roles', 'create')
def create_role():
    """Create a new role"""
    try:
        if not user_has_component('roles'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.json
        
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        
        if Role.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'Role already exists'}), 400
        
        role = Role(
            name=data['name'],
            description=data.get('description'),
            is_system=False,
            is_active=True,
            created_by_id=current_user.id
        )
        db.session.add(role)
        db.session.commit()
        
        component_ids = data.get('component_ids', [])
        for comp_id in component_ids:
            component = DashboardComponent.query.get(comp_id)
            if component:
                rc = RoleComponent(role_id=role.id, component_id=comp_id)
                db.session.add(rc)
        
        db.session.commit()
        return jsonify({'message': 'Role created', 'role': role.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/roles/<int:id>', methods=['PUT'])
@login_required
@require_permission('roles', 'update')
def update_role(id):
    """Update a role"""
    try:
        if not user_has_component('roles'):
            return jsonify({'error': 'Access denied'}), 403
        
        role = Role.query.get_or_404(id)
        data = request.json
        
        if role.is_system and data.get('name') != role.name:
            return jsonify({'error': 'Cannot modify system role name'}), 400
        
        if 'name' in data:
            role.name = data['name']
        if 'description' in data:
            role.description = data['description']
        if 'is_active' in data:
            role.is_active = data['is_active']
        
        if 'component_ids' in data:
            RoleComponent.query.filter_by(role_id=role.id).delete()
            for comp_id in data['component_ids']:
                component = DashboardComponent.query.get(comp_id)
                if component:
                    rc = RoleComponent(role_id=role.id, component_id=comp_id)
                    db.session.add(rc)
        
        db.session.commit()
        return jsonify({'message': 'Role updated', 'role': role.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/roles/<int:id>', methods=['DELETE'])
@login_required
@require_permission('roles', 'delete')
def delete_role(id):
    """Delete a role"""
    try:
        if not user_has_component('roles'):
            return jsonify({'error': 'Access denied'}), 403
        
        role = Role.query.get_or_404(id)
        
        if role.is_system:
            return jsonify({'error': 'Cannot delete system role'}), 400
        
        if role.users and len(role.users) > 0:
            return jsonify({'error': 'Cannot delete role with assigned users'}), 400
        
        db.session.delete(role)
        db.session.commit()
        return jsonify({'message': 'Role deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============================================================
# PERMISSIONS
# ============================================================

@admin_bp.route('/permissions/me', methods=['GET'])
@login_required
def get_my_permissions():
    """Get current user's permissions"""
    try:
        permissions = get_user_permissions(current_user)
        components = ComponentService.get_user_components()
        
        return jsonify({
            'permissions': permissions,
            'components': [c.to_dict() for c in components],
            'role': current_user.role,
            'user_id': current_user.id,
            'email': current_user.email,
            'full_name': current_user.full_name,
            'is_super_admin': current_user.is_super_admin()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/permissions/resources', methods=['GET'])
@login_required
@require_permission('permissions', 'read')
def get_permission_resources():
    """Get all resources with their actions"""
    try:
        from permission_service import COMPONENT_ACTION_MAP
        
        resources = []
        for key, actions in COMPONENT_ACTION_MAP.items():
            component = DashboardComponent.query.filter_by(key=key).first()
            resources.append({
                'name': key,
                'label': component.label if component else key.title(),
                'actions': actions
            })
        
        return jsonify(resources), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@admin_bp.route('/permissions/users/<int:user_id>', methods=['GET'])
@login_required
def get_user_permissions(user_id):
    """Get permissions for a specific user"""
    try:
        # Check if user has access to permissions component
        if not user_has_component('permissions'):
            return jsonify({'error': 'Access denied'}), 403
        
        # Only super admin can view other users' permissions
        if current_user.role != 'super_admin' and current_user.id != user_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        user = User.query.get_or_404(user_id)
        
        # Get custom permissions from database
        custom_perms = UserPermission.query.filter_by(user_id=user_id).all()
        
        # Get role defaults based on user's role
        from permission_service import ROLE_PERMISSIONS
        role_defaults = ROLE_PERMISSIONS.get(user.role, {})
        
        # Get effective permissions
        from permission_service import get_user_permissions
        effective_permissions = get_user_permissions(user)
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'is_active': user.is_active,
                'is_tour_manager': user.is_tour_manager,
                'is_tour_assistant': user.is_tour_assistant
            },
            'custom_permissions': [{
                'id': p.id,
                'resource': p.resource,
                'action': p.action,
                'is_allowed': p.is_allowed
            } for p in custom_perms],
            'role_defaults': role_defaults,
            'effective_permissions': effective_permissions
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/permissions/users/<int:user_id>', methods=['POST'])
@login_required
@require_permission('permissions', 'update')
def set_user_permission(user_id):
    """Set a custom permission for a user"""
    try:
        if not user_has_component('permissions'):
            return jsonify({'error': 'Access denied'}), 403
        
        if current_user.role != 'super_admin':
            return jsonify({'error': 'Super admin only'}), 403
        
        data = request.json
        resource = data.get('resource')
        action = data.get('action')
        is_allowed = data.get('is_allowed', True)
        
        if not resource or not action:
            return jsonify({'error': 'Resource and action required'}), 400
        
        # Check if permission already exists
        perm = UserPermission.query.filter_by(
            user_id=user_id,
            resource=resource,
            action=action
        ).first()
        
        if perm:
            perm.is_allowed = is_allowed
            perm.updated_at = datetime.utcnow()
        else:
            perm = UserPermission(
                user_id=user_id,
                resource=resource,
                action=action,
                is_allowed=is_allowed,
                created_by=current_user.id
            )
            db.session.add(perm)
        
        db.session.commit()
        
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='update',
            resource_type='permissions',
            resource_id=user_id,
            description=f'Set {resource}:{action} to {is_allowed} for user {user_id}'
        )
        
        return jsonify({'message': 'Permission set', 'id': perm.id}), 200
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/permissions/users/<int:user_id>/<int:perm_id>', methods=['DELETE'])
@login_required
@require_permission('permissions', 'delete')
def delete_user_permission(user_id, perm_id):
    """Delete a custom permission"""
    try:
        if not user_has_component('permissions'):
            return jsonify({'error': 'Access denied'}), 403
        
        if current_user.role != 'super_admin':
            return jsonify({'error': 'Super admin only'}), 403
        
        perm = UserPermission.query.get_or_404(perm_id)
        if perm.user_id != user_id:
            return jsonify({'error': 'Permission not found for this user'}), 404
        
        db.session.delete(perm)
        db.session.commit()
        
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='delete',
            resource_type='permissions',
            resource_id=user_id,
            description=f'Deleted permission for user {user_id}'
        )
        
        return jsonify({'message': 'Permission removed'}), 200
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



# ============================================================
# ACTIVITIES
# ============================================================

@admin_bp.route('/activities', methods=['GET'])
@login_required
def get_activities():
    """Get user's activities"""
    try:
        if not user_has_component('activities'):
            return jsonify({'error': 'Access denied'}), 403
        
        limit = request.args.get('limit', 20, type=int)
        
        if current_user.role == 'super_admin':
            activities = ActivityLog.query.order_by(
                ActivityLog.created_at.desc()
            ).limit(limit).all()
        else:
            activities = ActivityLog.query.filter_by(
                user_id=current_user.id
            ).order_by(
                ActivityLog.created_at.desc()
            ).limit(limit).all()
        
        return jsonify({
            'activities': [a.to_dict() for a in activities]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500












# ============================================================
# UPLOAD ROUTES
# ============================================================

@admin_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """Upload a file"""
    try:
        from werkzeug.utils import secure_filename
        from app import allowed_file, app
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        folder = request.form.get('folder', 'general')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        safe_folder = secure_filename(folder)
        target_dir = os.path.join(app.config['UPLOAD_FOLDER'], safe_folder)
        os.makedirs(target_dir, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{secure_filename(file.filename)}"
        filepath = os.path.join(target_dir, filename)
        file.save(filepath)
        
        return jsonify({
            'url': f"/uploads/{safe_folder}/{filename}",
            'filename': filename,
            'message': 'File uploaded successfully'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@admin_bp.route('/referral/links', methods=['GET'])
@login_required
def get_referral_links():
    """Get all referral links"""
    try:
        if not user_has_component('partner-links'):
            return jsonify({'error': 'Access denied'}), 403
        
        links = ReferralLink.query.order_by(ReferralLink.created_at.desc()).all()
        return jsonify([l.to_dict() for l in links]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/referral/links', methods=['POST'])
@login_required
@require_permission('partner-links', 'create')
def create_referral_link():
    """Create a new referral link"""
    try:
        if not user_has_component('partner-links'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.json
        
        link = ReferralLink(
            user_id=current_user.id,
            name=data.get('name'),
            destination_url=data.get('destination_url'),
            campaign_name=data.get('campaign_name'),
            is_active=data.get('is_active', True)
        )
        link.generate_code()
        db.session.add(link)
        db.session.commit()
        
        return jsonify({'message': 'Link created', 'link': link.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/referral/links/<int:link_id>', methods=['PUT'])
@login_required
@require_permission('partner-links', 'update')
def update_referral_link(link_id):
    """Update a referral link"""
    try:
        if not user_has_component('partner-links'):
            return jsonify({'error': 'Access denied'}), 403
        
        link = ReferralLink.query.get_or_404(link_id)
        data = request.json
        
        if 'name' in data:
            link.name = data['name']
        if 'destination_url' in data:
            link.destination_url = data['destination_url']
        if 'campaign_name' in data:
            link.campaign_name = data['campaign_name']
        if 'is_active' in data:
            link.is_active = data['is_active']
        
        db.session.commit()
        return jsonify({'message': 'Link updated', 'link': link.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/referral/links/<int:link_id>', methods=['DELETE'])
@login_required
@require_permission('partner-links', 'delete')
def delete_referral_link(link_id):
    """Delete a referral link"""
    try:
        if not user_has_component('partner-links'):
            return jsonify({'error': 'Access denied'}), 403
        
        link = ReferralLink.query.get_or_404(link_id)
        db.session.delete(link)
        db.session.commit()
        return jsonify({'message': 'Link deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/referral/links/<int:link_id>/clicks', methods=['GET'])
@login_required
def get_referral_clicks(link_id):
    """Get clicks for a referral link"""
    try:
        if not user_has_component('partner-analytics'):
            return jsonify({'error': 'Access denied'}), 403
        
        link = ReferralLink.query.get_or_404(link_id)
        days = request.args.get('days', 30, type=int)
        
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        
        clicks = ReferralClick.query.filter(
            ReferralClick.link_id == link_id,
            ReferralClick.clicked_at >= start_date
        ).order_by(ReferralClick.clicked_at.desc()).all()
        
        return jsonify({
            'link': link.to_dict(),
            'clicks': [c.to_dict() for c in clicks],
            'total': len(clicks)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/referral/links/<int:link_id>/convert', methods=['POST'])
@login_required
@require_permission('partner-links', 'update')
def convert_referral_link(link_id):
    """Record a conversion for a referral link"""
    try:
        if not user_has_component('partner-links'):
            return jsonify({'error': 'Access denied'}), 403
        
        link = ReferralLink.query.get_or_404(link_id)
        link.record_conversion()
        
        return jsonify({'message': 'Conversion recorded', 'link': link.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/referral/stats', methods=['GET'])
@login_required
def get_referral_stats():
    """Get referral statistics"""
    try:
        if not user_has_component('partner-analytics'):
            return jsonify({'error': 'Access denied'}), 403
        
        total_links = ReferralLink.query.count()
        total_clicks = db.session.query(db.func.sum(ReferralLink.total_clicks)).scalar() or 0
        total_conversions = db.session.query(db.func.sum(ReferralLink.conversions)).scalar() or 0
        
        return jsonify({
            'total_links': total_links,
            'total_clicks': total_clicks,
            'total_conversions': total_conversions,
            'conversion_rate': round((total_conversions / total_clicks * 100), 2) if total_clicks > 0 else 0
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/referral/top-links', methods=['GET'])
@login_required
def get_top_referral_links():
    """Get top referral links"""
    try:
        if not user_has_component('partner-analytics'):
            return jsonify({'error': 'Access denied'}), 403
        
        limit = request.args.get('limit', 3, type=int)
        sort_by = request.args.get('sort_by', 'clicks')
        
        if sort_by == 'clicks':
            links = ReferralLink.query.order_by(ReferralLink.total_clicks.desc()).limit(limit).all()
        elif sort_by == 'conversions':
            links = ReferralLink.query.order_by(ReferralLink.conversions.desc()).limit(limit).all()
        else:
            links = ReferralLink.query.order_by(ReferralLink.created_at.desc()).limit(limit).all()
        
        return jsonify([l.to_dict() for l in links]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@admin_bp.route('/referral/partner/<int:partner_id>/stats', methods=['GET'])
@login_required
def get_partner_stats(partner_id):
    """Get stats for a specific partner"""
    try:
        if not user_has_component('partners'):
            return jsonify({'error': 'Access denied'}), 403
        
        partner = User.query.get_or_404(partner_id)
        
        # Check if user is actually a partner
        if partner.role != 'partner':
            return jsonify({'error': 'User is not a partner'}), 400
        
        # Get referral links for this partner
        links = ReferralLink.query.filter_by(user_id=partner_id).all()
        
        total_links = len(links)
        total_clicks = sum(link.total_clicks for link in links) if links else 0
        total_conversions = sum(link.conversions for link in links) if links else 0
        total_unique_clicks = sum(link.unique_clicks for link in links) if links else 0
        
        # Get recent links (last 5)
        recent_links = ReferralLink.query.filter_by(user_id=partner_id)\
            .order_by(ReferralLink.created_at.desc())\
            .limit(5).all()
        
        return jsonify({
            'partner_id': partner.id,
            'full_name': partner.full_name,
            'email': partner.email,
            'referral_code': partner.referral_code,
            'is_active': partner.is_active,
            'total_links': total_links,
            'total_clicks': total_clicks,
            'total_conversions': total_conversions,
            'total_unique_clicks': total_unique_clicks,
            'conversion_rate': round((total_conversions / total_clicks * 100), 2) if total_clicks > 0 else 0,
            'links': [l.to_dict() for l in recent_links]
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/referral/partners', methods=['GET'])
@login_required
def get_all_partners():
    """Get all partners with their stats"""
    try:
        if not user_has_component('partners'):
            return jsonify({'error': 'Access denied'}), 403
        
        partners = User.query.filter_by(role='partner').order_by(User.full_name).all()
        
        result = []
        for partner in partners:
            links = ReferralLink.query.filter_by(user_id=partner.id).all()
            total_clicks = sum(link.total_clicks for link in links) if links else 0
            total_conversions = sum(link.conversions for link in links) if links else 0
            
            result.append({
                'id': partner.id,
                'full_name': partner.full_name,
                'email': partner.email,
                'referral_code': partner.referral_code,
                'is_active': partner.is_active,
                'total_links': len(links),
                'total_clicks': total_clicks,
                'total_conversions': total_conversions,
                'conversion_rate': round((total_conversions / total_clicks * 100), 2) if total_clicks > 0 else 0,
                'created_at': partner.created_at.isoformat() if partner.created_at else None
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



@admin_bp.route('/referral/partners/all', methods=['GET'])
@login_required
def get_all_partners_with_stats():
    """Get all partners with their stats"""
    try:
        if not user_has_component('partners'):
            return jsonify({'error': 'Access denied'}), 403
        
        partners = User.query.filter_by(role='partner').order_by(User.full_name).all()
        
        result = []
        for partner in partners:
            links = ReferralLink.query.filter_by(user_id=partner.id).all()
            total_clicks = sum(link.total_clicks for link in links) if links else 0
            total_conversions = sum(link.conversions for link in links) if links else 0
            total_unique_clicks = sum(link.unique_clicks for link in links) if links else 0
            
            result.append({
                'id': partner.id,
                'full_name': partner.full_name,
                'email': partner.email,
                'referral_code': partner.referral_code,
                'is_active': partner.is_active,
                'total_links': len(links),
                'total_clicks': total_clicks,
                'total_conversions': total_conversions,
                'total_unique_clicks': total_unique_clicks,
                'conversion_rate': round((total_conversions / total_clicks * 100), 2) if total_clicks > 0 else 0,
                'created_at': partner.created_at.isoformat() if partner.created_at else None,
                'links': [l.to_dict() for l in links[:5]]  # Show last 5 links
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



@admin_bp.route('/referral/partner/<int:partner_id>/links', methods=['POST'])
@login_required
@require_permission('partner-links', 'create')
def create_partner_link(partner_id):
    """Create a referral link for a specific partner"""
    try:
        if not user_has_component('partner-links'):
            return jsonify({'error': 'Access denied'}), 403
        
        partner = User.query.get_or_404(partner_id)
        
        if partner.role != 'partner':
            return jsonify({'error': 'User is not a partner'}), 400
        
        data = request.json
        
        link = ReferralLink(
            user_id=partner_id,
            name=data.get('name'),
            destination_url=data.get('destination_url'),
            campaign_name=data.get('campaign_name'),
            is_active=data.get('is_active', True)
        )
        link.generate_code()
        db.session.add(link)
        db.session.commit()
        
        return jsonify({'message': 'Link created', 'link': link.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500




@admin_bp.route('/referral/analytics', methods=['GET'])
@login_required
def get_referral_analytics():
    """Get referral analytics"""
    try:
        if not user_has_component('partner-analytics'):
            return jsonify({'error': 'Access denied'}), 403
        
        total_links = ReferralLink.query.count()
        total_clicks = db.session.query(db.func.sum(ReferralLink.total_clicks)).scalar() or 0
        total_conversions = db.session.query(db.func.sum(ReferralLink.conversions)).scalar() or 0
        
        # Get recent links
        recent_links = ReferralLink.query.order_by(ReferralLink.created_at.desc()).limit(5).all()
        
        return jsonify({
            'total_links': total_links,
            'total_clicks': total_clicks,
            'total_conversions': total_conversions,
            'conversion_rate': round((total_conversions / total_clicks * 100), 2) if total_clicks > 0 else 0,
            'recent_links': [l.to_dict() for l in recent_links]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500









