# backend/job_routes.py
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Job, JobCategory, JobApplication, User
from datetime import datetime
import re
import secrets
from werkzeug.utils import secure_filename
import os
from email_service import EmailService






# Initialize email service
email_service = EmailService()

job_bp = Blueprint('job', __name__)

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
        print(f"Error logging activity: {e}")
        db.session.rollback()

# ========== PUBLIC JOB ROUTES ==========

@job_bp.route('/jobs', methods=['GET'])
def get_jobs():
    """Get all active jobs"""
    try:
        category = request.args.get('category')
        job_type = request.args.get('type')
        search = request.args.get('search')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = Job.query.filter_by(is_active=True)
        
        if category and category != 'all':
            query = query.filter_by(category_id=category)
        if job_type and job_type != 'all':
            query = query.filter_by(type=job_type)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Job.title.ilike(search_term),
                    Job.description.ilike(search_term),
                    Job.requirements.ilike(search_term)
                )
            )
        
        # Filter by deadline
        query = query.filter(
            db.or_(
                Job.application_deadline.is_(None),
                Job.application_deadline >= datetime.utcnow()
            )
        )
        
        paginated = query.order_by(Job.is_featured.desc(), Job.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'data': [{
                'id': j.id,
                'title': j.title,
                'slug': j.slug,
                'category': {
                    'id': j.category.id,
                    'name': j.category.name
                } if j.category else None,
                'location': j.location,
                'type': j.type,
                'experience_level': j.experience_level,
                'salary_range': j.salary_range,
                'description': j.description[:200] + '...' if len(j.description) > 200 else j.description,
                'requirements': j.requirements[:200] + '...' if len(j.requirements) > 200 else j.requirements,
                'is_featured': j.is_featured,
                'application_deadline': j.application_deadline.isoformat() if j.application_deadline else None,
                'created_at': j.created_at.isoformat()
            } for j in paginated.items],
            'pagination': {
                'current_page': paginated.page,
                'total_pages': paginated.pages,
                'total_items': paginated.total,
                'has_next': paginated.has_next,
                'has_prev': paginated.has_prev
            }
        }), 200
    except Exception as e:
        print(f"Error in get_jobs: {e}")
        return jsonify({'error': str(e)}), 500

@job_bp.route('/jobs/<slug>', methods=['GET'])
def get_job(slug):
    """Get single job by slug"""
    try:
        job = Job.query.filter_by(slug=slug, is_active=True).first_or_404()
        
        # Increment view count
        job.views_count += 1
        db.session.commit()
        
        return jsonify({
            'id': job.id,
            'title': job.title,
            'slug': job.slug,
            'category': {
                'id': job.category.id,
                'name': job.category.name
            } if job.category else None,
            'location': job.location,
            'type': job.type,
            'experience_level': job.experience_level,
            'salary_range': job.salary_range,
            'description': job.description,
            'requirements': job.requirements,
            'responsibilities': job.responsibilities,
            'benefits': job.benefits,
            'application_deadline': job.application_deadline.isoformat() if job.application_deadline else None,
            'is_active': job.is_active,
            'views_count': job.views_count,
            'created_at': job.created_at.isoformat()
        }), 200
    except Exception as e:
        print(f"Error in get_job: {e}")
        return jsonify({'error': 'Job not found'}), 404

@job_bp.route('/jobs/<int:job_id>/apply', methods=['POST'])
def apply_for_job(job_id):
    """Submit job application (public) with email confirmation"""
    try:
        job = Job.query.get_or_404(job_id)
        
        # Check if job is still accepting applications
        if not job.is_active:
            return jsonify({'error': 'This job is no longer accepting applications'}), 400
        
        if job.application_deadline and job.application_deadline < datetime.utcnow():
            return jsonify({'error': 'Application deadline has passed'}), 400
        
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        cover_letter = request.form.get('cover_letter', '').strip()
        portfolio_url = request.form.get('portfolio_url', '').strip()
        linkedin_url = request.form.get('linkedin_url', '').strip()
        
        # Validate
        if not first_name or not last_name:
            return jsonify({'error': 'First name and last name are required'}), 400
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({'error': 'Invalid email format'}), 400
        if not cover_letter:
            return jsonify({'error': 'Cover letter is required'}), 400
        
        # Check if already applied
        existing = JobApplication.query.filter_by(job_id=job_id, email=email).first()
        if existing:
            return jsonify({'error': 'You have already applied for this position'}), 400
        
        # Handle CV upload
        if 'cv' not in request.files:
            return jsonify({'error': 'CV file is required'}), 400
        
        cv_file = request.files['cv']
        if cv_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(cv_file.filename):
            return jsonify({'error': 'Invalid file type. Please upload PDF, DOC, or DOCX'}), 400
        
        # Secure filename and save
        original_filename = secure_filename(cv_file.filename)
        name, ext = os.path.splitext(original_filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        random_suffix = secrets.token_urlsafe(4)
        filename = f"cv_{job_id}_{timestamp}_{random_suffix}{ext}"
        
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'job_applications')
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, filename)
        cv_file.save(filepath)
        
        cv_url = f"/uploads/job_applications/{filename}"
        
        # Create application
        application = JobApplication(
            job_id=job_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            cover_letter=cover_letter,
            cv_url=cv_url,
            portfolio_url=portfolio_url,
            linkedin_url=linkedin_url,
            status='pending',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        
        db.session.add(application)
        
        # Increment applications count
        job.applications_count += 1
        
        db.session.commit()
        
        # ========== SEND EMAIL CONFIRMATION TO APPLICANT ==========
        try:
            email_service.send_job_application_confirmation(
                f"{first_name} {last_name}",
                email,
                job.title,
                application.id
            )
            print(f"✅ Confirmation email sent to {email}")
        except Exception as e:
            print(f"❌ Error sending confirmation email: {e}")
        
        # ========== SEND NOTIFICATION TO ALL ADMINS ==========
        try:
            admins = User.query.filter(User.role.in_(['admin', 'super_admin'])).all()
            for admin in admins:
                if admin.email:
                    email_service.send_admin_job_notification(
                        admin.email,
                        admin.full_name,
                        f"{first_name} {last_name}",
                        job.title,
                        application.id
                    )
            print(f"✅ Admin notifications sent to {len(admins)} admins")
        except Exception as e:
            print(f"❌ Error sending admin notifications: {e}")
        
        return jsonify({
            'message': 'Application submitted successfully',
            'application_id': application.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in apply_for_job: {e}")
        return jsonify({'error': str(e)}), 500

# ========== PUBLIC JOB CATEGORIES ==========

@job_bp.route('/job-categories', methods=['GET'])
def get_job_categories():
    """Get all active job categories"""
    try:
        categories = JobCategory.query.filter_by(is_active=True).all()
        
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'slug': c.slug,
            'description': c.description,
            'icon': c.icon,
            'job_count': len([j for j in c.jobs if j.is_active])
        } for c in categories]), 200
    except Exception as e:
        print(f"Error in get_job_categories: {e}")
        return jsonify([]), 200

# ========== ADMIN JOB ROUTES ==========

@job_bp.route('/admin/jobs', methods=['GET'])
@login_required

def admin_get_jobs():
    """Get all jobs for admin panel"""
    try:
        if current_user.role not in ['super_admin', 'admin']:
            return jsonify({'error': 'Permission denied'}), 403
        
        jobs = Job.query.order_by(Job.created_at.desc()).all()
        
        return jsonify([{
            'id': j.id,
            'title': j.title,
            'slug': j.slug,
            'category_id': j.category_id,
            'category_name': j.category.name if j.category else None,
            'location': j.location,
            'type': j.type,
            'experience_level': j.experience_level,
            'is_active': j.is_active,
            'is_featured': j.is_featured,
            'applications_count': j.applications_count,
            'views_count': j.views_count,
            'application_deadline': j.application_deadline.isoformat() if j.application_deadline else None,
            'created_at': j.created_at.isoformat(),
            'created_by': j.created_by_user.full_name if j.created_by_user else None
        } for j in jobs]), 200
    except Exception as e:
        print(f"Error in admin_get_jobs: {e}")
        return jsonify([]), 200

@job_bp.route('/admin/jobs', methods=['POST'])
@login_required

def admin_create_job():
    """Create a new job posting"""
    try:
        if current_user.role not in ['super_admin', 'admin']:
            return jsonify({'error': 'Permission denied'}), 403
        
        data = request.json
        
        # Generate slug
        slug = data.get('slug', '').strip()
        if not slug:
            slug = data['title'].lower().replace(' ', '-').replace('/', '-')
            # Make unique
            while Job.query.filter_by(slug=slug).first():
                slug = f"{slug}-{secrets.token_urlsafe(3)}"
        
        deadline = None
        if data.get('application_deadline'):
            deadline = datetime.fromisoformat(data.get('application_deadline').replace('Z', '+00:00'))
        
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
            application_deadline=deadline,
            is_active=data.get('is_active', True),
            is_featured=data.get('is_featured', False),
            created_by=current_user.id
        )
        
        db.session.add(job)
        db.session.commit()
        
        # Log activity
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='create',
            resource_type='job',
            resource_id=job.id,
            description=f'Created job posting: {job.title}'
        )
        
        return jsonify({'message': 'Job created', 'id': job.id, 'slug': job.slug}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating job: {e}")
        return jsonify({'error': str(e)}), 500

@job_bp.route('/admin/jobs/<int:job_id>', methods=['PUT'])
@login_required

def admin_update_job(job_id):
    """Update a job posting"""
    try:
        if current_user.role not in ['super_admin', 'admin']:
            return jsonify({'error': 'Permission denied'}), 403
        
        job = Job.query.get_or_404(job_id)
        data = request.json
        
        updatable_fields = ['title', 'category_id', 'location', 'type', 'experience_level', 
                           'salary_range', 'description', 'requirements', 'responsibilities', 
                           'benefits', 'is_active', 'is_featured']
        
        for field in updatable_fields:
            if field in data:
                setattr(job, field, data[field])
        
        if 'application_deadline' in data and data['application_deadline']:
            job.application_deadline = datetime.fromisoformat(data['application_deadline'].replace('Z', '+00:00'))
        elif 'application_deadline' in data and data['application_deadline'] is None:
            job.application_deadline = None
        
        if 'slug' in data and data['slug']:
            # Check if slug is unique
            existing = Job.query.filter_by(slug=data['slug']).first()
            if existing and existing.id != job_id:
                return jsonify({'error': 'Slug already exists'}), 400
            job.slug = data['slug']
        
        job.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='update',
            resource_type='job',
            resource_id=job.id,
            description=f'Updated job posting: {job.title}'
        )
        
        return jsonify({'message': 'Job updated'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@job_bp.route('/admin/jobs/<int:job_id>', methods=['DELETE'])
@login_required
def admin_delete_job(job_id):
    """Delete a job posting (soft delete)"""
    try:
        if current_user.role not in ['super_admin', 'admin']:
            return jsonify({'error': 'Permission denied'}), 403
        
        job = Job.query.get_or_404(job_id)
        
        # Soft delete - just mark inactive
        job.is_active = False
        db.session.commit()
        
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='delete',
            resource_type='job',
            resource_id=job.id,
            description=f'Soft deleted job posting: {job.title}'
        )
        
        return jsonify({'message': 'Job deleted'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ========== ADMIN JOB CATEGORY ROUTES ==========

@job_bp.route('/admin/job-categories', methods=['GET'])
@login_required
def admin_get_categories():
    """Get all job categories"""
    try:
        if current_user.role not in ['super_admin', 'admin']:
            return jsonify({'error': 'Permission denied'}), 403
        
        categories = JobCategory.query.order_by(JobCategory.name).all()
        
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'slug': c.slug,
            'description': c.description,
            'icon': c.icon,
            'is_active': c.is_active,
            'job_count': len(c.jobs)
        } for c in categories]), 200
    except Exception as e:
        print(f"Error in admin_get_categories: {e}")
        return jsonify([]), 200

@job_bp.route('/admin/job-categories', methods=['POST'])
@login_required
def admin_create_category():
    """Create a job category"""
    try:
        if current_user.role not in ['super_admin', 'admin']:
            return jsonify({'error': 'Permission denied'}), 403
        
        data = request.json
        
        slug = data.get('slug', '').strip()
        if not slug:
            slug = data['name'].lower().replace(' ', '-')
        
        # Check if slug exists
        if JobCategory.query.filter_by(slug=slug).first():
            return jsonify({'error': 'Category with this slug already exists'}), 400
        
        category = JobCategory(
            name=data['name'],
            slug=slug,
            description=data.get('description'),
            icon=data.get('icon'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(category)
        db.session.commit()
        
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='create',
            resource_type='job_category',
            resource_id=category.id,
            description=f'Created job category: {category.name}'
        )
        
        return jsonify({'message': 'Category created', 'id': category.id}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@job_bp.route('/admin/job-categories/<int:category_id>', methods=['PUT'])
@login_required
def admin_update_category(category_id):
    """Update a job category"""
    try:
        if current_user.role not in ['super_admin', 'admin']:
            return jsonify({'error': 'Permission denied'}), 403
        
        category = JobCategory.query.get_or_404(category_id)
        data = request.json
        
        if 'name' in data:
            category.name = data['name']
        if 'slug' in data:
            # Check if slug is unique
            existing = JobCategory.query.filter_by(slug=data['slug']).first()
            if existing and existing.id != category_id:
                return jsonify({'error': 'Slug already exists'}), 400
            category.slug = data['slug']
        if 'description' in data:
            category.description = data['description']
        if 'icon' in data:
            category.icon = data['icon']
        if 'is_active' in data:
            category.is_active = data['is_active']
        
        db.session.commit()
        
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='update',
            resource_type='job_category',
            resource_id=category.id,
            description=f'Updated job category: {category.name}'
        )
        
        return jsonify({'message': 'Category updated'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@job_bp.route('/admin/job-categories/<int:category_id>', methods=['DELETE'])
@login_required
def admin_delete_category(category_id):
    """Delete a job category"""
    try:
        if current_user.role != 'super_admin':
            return jsonify({'error': 'Super admin access required'}), 403
        
        category = JobCategory.query.get_or_404(category_id)
        
        # Check if category has jobs
        if category.jobs:
            return jsonify({'error': 'Cannot delete category with existing jobs'}), 400
        
        db.session.delete(category)
        db.session.commit()
        
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='delete',
            resource_type='job_category',
            resource_id=category_id,
            description=f'Deleted job category: {category.name}'
        )
        
        return jsonify({'message': 'Category deleted'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ========== ADMIN JOB APPLICATION ROUTES ==========

@job_bp.route('/admin/applications', methods=['GET'])
@login_required
def admin_get_applications():
    """Get all job applications"""
    try:
        if current_user.role not in ['super_admin', 'admin']:
            return jsonify({'error': 'Permission denied'}), 403
        
        job_id = request.args.get('job_id', type=int)
        status = request.args.get('status')
        
        query = JobApplication.query
        
        if job_id:
            query = query.filter_by(job_id=job_id)
        if status:
            query = query.filter_by(status=status)
        
        applications = query.order_by(JobApplication.applied_at.desc()).all()
        
        return jsonify([{
            'id': a.id,
            'job_title': a.job.title,
            'job_id': a.job_id,
            'applicant_name': a.get_full_name(),
            'first_name': a.first_name,
            'last_name': a.last_name,
            'email': a.email,
            'phone': a.phone,
            'cover_letter': a.cover_letter[:200] + '...' if len(a.cover_letter) > 200 else a.cover_letter,
            'cv_url': a.cv_url,
            'portfolio_url': a.portfolio_url,
            'linkedin_url': a.linkedin_url,
            'status': a.status,
            'status_display': a.status.capitalize(),
            'admin_notes': a.admin_notes,
            'rating': a.rating,
            'admin_reply': a.admin_reply,
            'replied_at': a.replied_at.isoformat() if a.replied_at else None,
            'applied_at': a.applied_at.isoformat()
        } for a in applications]), 200
    except Exception as e:
        print(f"Error in admin_get_applications: {e}")
        return jsonify([]), 200

@job_bp.route('/admin/applications/<int:application_id>', methods=['GET'])
@login_required
def admin_get_application(application_id):
    """Get single application details"""
    try:
        if current_user.role not in ['super_admin', 'admin']:
            return jsonify({'error': 'Permission denied'}), 403
        
        app = JobApplication.query.get_or_404(application_id)
        
        return jsonify({
            'id': app.id,
            'job_title': app.job.title,
            'job_id': app.job_id,
            'first_name': app.first_name,
            'last_name': app.last_name,
            'email': app.email,
            'phone': app.phone,
            'cover_letter': app.cover_letter,
            'cv_url': app.cv_url,
            'portfolio_url': app.portfolio_url,
            'linkedin_url': app.linkedin_url,
            'status': app.status,
            'admin_notes': app.admin_notes,
            'rating': app.rating,
            'admin_reply': app.admin_reply,
            'replied_at': app.replied_at.isoformat() if app.replied_at else None,
            'replied_by': app.replied_by_user.full_name if app.replied_by_user else None,
            'applied_at': app.applied_at.isoformat(),
            'ip_address': app.ip_address,
            'user_agent': app.user_agent
        }), 200
    except Exception as e:
        print(f"Error in admin_get_application: {e}")
        return jsonify({'error': str(e)}), 500

@job_bp.route('/admin/applications/<int:application_id>/status', methods=['PUT'])
@login_required
def admin_update_application_status(application_id):
    """Update application status with email notification"""
    try:
        if current_user.role not in ['super_admin', 'admin']:
            return jsonify({'error': 'Permission denied'}), 403
        
        app = JobApplication.query.get_or_404(application_id)
        data = request.json
        
        valid_statuses = ['pending', 'reviewed', 'shortlisted', 'rejected', 'hired']
        old_status = app.status
        
        if 'status' in data:
            if data['status'] not in valid_statuses:
                return jsonify({'error': 'Invalid status'}), 400
            app.status = data['status']
        if 'admin_notes' in data:
            app.admin_notes = data['admin_notes']
        if 'rating' in data:
            app.rating = data['rating']
        
        app.updated_at = datetime.utcnow()
        db.session.commit()
        
        # ========== SEND EMAIL NOTIFICATION IF STATUS CHANGED ==========
        if old_status != app.status and app.status != 'pending':
            try:
                notes = data.get('admin_notes', None)
                email_service.send_job_status_update(
                    app.get_full_name(),
                    app.email,
                    app.job.title,
                    app.status,
                    notes
                )
                print(f"✅ Status update email sent to {app.email} for status: {app.status}")
            except Exception as e:
                print(f"❌ Error sending status update email: {e}")
        
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='update',
            resource_type='job_application',
            resource_id=app.id,
            description=f'Updated application status to {app.status} for {app.get_full_name()}'
        )
        
        return jsonify({'message': 'Application updated'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@job_bp.route('/admin/applications/<int:application_id>/reply', methods=['POST'])
@login_required
def admin_reply_application(application_id):
    """Reply to job application with email notification"""
    try:
        if current_user.role not in ['super_admin', 'admin']:
            return jsonify({'error': 'Permission denied'}), 403
        
        app = JobApplication.query.get_or_404(application_id)
        data = request.json
        
        reply_message = data.get('reply', '').strip()
        
        if not reply_message:
            return jsonify({'error': 'Reply message is required'}), 400
        
        app.admin_reply = reply_message
        app.replied_at = datetime.utcnow()
        app.replied_by = current_user.id
        
        db.session.commit()
        
        # ========== SEND REPLY EMAIL TO APPLICANT ==========
        try:
            email_service.send_job_admin_reply(
                app.get_full_name(),
                app.email,
                app.job.title,
                reply_message
            )
            print(f"✅ Reply email sent to {app.email}")
        except Exception as e:
            print(f"❌ Error sending reply email: {e}")
        
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='reply',
            resource_type='job_application',
            resource_id=app.id,
            description=f'Replied to application from {app.get_full_name()}'
        )
        
        return jsonify({'message': 'Reply sent successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500