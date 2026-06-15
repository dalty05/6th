# backend/blog_routes.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, BlogPost, User, ActivityLog
from datetime import datetime
import re





blog_bp = Blueprint('blog', __name__)

def log_activity(user_id, user_name, action, resource_type, resource_id, description):
    """Log user activity"""
    try:
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

# ========== PUBLIC BLOG ROUTES ==========

@blog_bp.route('/blog', methods=['GET'])
def get_blog_posts():
    """Get published blog posts for public viewing"""
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

@blog_bp.route('/blog/<slug>', methods=['GET'])
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

# ========== ADMIN BLOG ROUTES ==========

@blog_bp.route('/admin/blog', methods=['GET'])
@login_required
def admin_get_blog_posts():
    """Get all blog posts for admin panel (with status filtering)"""
    try:
        if current_user.role == 'super_admin':
            # Super admin sees all posts
            posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
        else:
            # Admin sees: their own drafts + all published posts
            posts = BlogPost.query.filter(
                (BlogPost.status == 'published') | (BlogPost.author_id == current_user.id)
            ).order_by(BlogPost.created_at.desc()).all()
        
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
            'can_edit': current_user.role == 'super_admin' or p.author_id == current_user.id,
            'can_publish': current_user.role == 'super_admin' and p.status == 'draft'
        } for p in posts]), 200
    except Exception as e:
        print(f"Error in admin_get_blog_posts: {e}")
        return jsonify([]), 200

@blog_bp.route('/admin/blog', methods=['POST'])
@login_required
def create_blog_post():
    """Create a new blog post (draft for admin, published for super admin)"""
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
        
        # Set status based on role
        if current_user.role == 'super_admin':
            status = data.get('status', 'published')
        else:
            status = 'draft'  # Admin creates as draft
        
        post = BlogPost(
            title=data['title'],
            slug=data['slug'],
            excerpt=data.get('excerpt', ''),
            content=data['content'],
            featured_image=data.get('featured_image', ''),
            status=status,
            author_id=current_user.id
        )
        
        db.session.add(post)
        db.session.commit()
        
        # Log activity
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='create',
            resource_type='blog',
            resource_id=post.id,
            description=f'Created blog post: {post.title} (Status: {status})'
        )
        
        return jsonify({
            'message': 'Blog post created',
            'id': post.id,
            'status': status
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating blog post: {str(e)}")
        return jsonify({'error': str(e)}), 500

@blog_bp.route('/admin/blog/<int:id>', methods=['PUT'])
@login_required
def update_blog_post(id):
    """Update an existing blog post"""
    try:
        post = BlogPost.query.get_or_404(id)
        
        # Check permission: only author or super admin can edit
        if current_user.role != 'super_admin' and post.author_id != current_user.id:
            return jsonify({'error': 'You can only edit your own blog posts'}), 403
        
        data = request.json
        
        # Update allowed fields
        allowed_fields = ['title', 'slug', 'excerpt', 'content', 'featured_image']
        
        # Check if slug changed and validate uniqueness
        if 'slug' in data and data['slug'] != post.slug:
            existing = BlogPost.query.filter_by(slug=data['slug']).first()
            if existing:
                return jsonify({'error': 'Slug already exists'}), 400
            post.slug = data['slug']
        
        for key, value in data.items():
            if key in allowed_fields and hasattr(post, key):
                setattr(post, key, value)
        
        post.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log activity
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

@blog_bp.route('/admin/blog/<int:id>/publish', methods=['POST'])
@login_required
def publish_blog_post(id):
    """Publish a draft blog post (Super Admin only)"""
    try:
        # Check if user is super admin
        if current_user.role != 'super_admin':
            return jsonify({'error': 'Only super admin can publish blog posts'}), 403
        
        post = BlogPost.query.get_or_404(id)
        
        if post.status == 'published':
            return jsonify({'error': 'Blog post is already published'}), 400
        
        # Update status
        post.status = 'published'
        post.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log activity
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='publish',
            resource_type='blog',
            resource_id=post.id,
            description=f'Published blog post: {post.title}'
        )
        
        return jsonify({'message': 'Blog post published successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error publishing blog post: {str(e)}")
        return jsonify({'error': str(e)}), 500

@blog_bp.route('/admin/blog/<int:id>/unpublish', methods=['POST'])
@login_required
def unpublish_blog_post(id):
    """Unpublish a blog post (Super Admin only)"""
    try:
        if current_user.role != 'super_admin':
            return jsonify({'error': 'Only super admin can unpublish blog posts'}), 403
        
        post = BlogPost.query.get_or_404(id)
        
        if post.status == 'draft':
            return jsonify({'error': 'Blog post is already a draft'}), 400
        
        post.status = 'draft'
        post.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='unpublish',
            resource_type='blog',
            resource_id=post.id,
            description=f'Unpublished blog post: {post.title}'
        )
        
        return jsonify({'message': 'Blog post unpublished successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error unpublishing blog post: {str(e)}")
        return jsonify({'error': str(e)}), 500

@blog_bp.route('/admin/blog/<int:id>', methods=['DELETE'])
@login_required
def delete_blog_post(id):
    """Delete a blog post (Super Admin only, or author if draft)"""
    try:
        post = BlogPost.query.get_or_404(id)
        
        # Check permission
        if current_user.role != 'super_admin':
            # Regular admin can only delete their own draft posts
            if post.status != 'draft' or post.author_id != current_user.id:
                return jsonify({'error': 'You can only delete your own draft posts'}), 403
        
        post_title = post.title
        db.session.delete(post)
        db.session.commit()
        
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

@blog_bp.route('/admin/blog/<int:id>/status', methods=['PUT'])
@login_required
def update_blog_status(id):
    """Update blog post status (Super Admin only)"""
    try:
        if current_user.role != 'super_admin':
            return jsonify({'error': 'Only super admin can change post status'}), 403
        
        post = BlogPost.query.get_or_404(id)
        data = request.json
        new_status = data.get('status')
        
        if new_status not in ['published', 'draft']:
            return jsonify({'error': 'Invalid status'}), 400
        
        post.status = new_status
        post.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='status_change',
            resource_type='blog',
            resource_id=post.id,
            description=f'Changed blog post status to {new_status}: {post.title}'
        )
        
        return jsonify({'message': f'Blog post {new_status}'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ========== BLOG IMAGE UPLOAD ==========

@blog_bp.route('/admin/blog/<int:id>/upload-image', methods=['POST'])
@login_required
def upload_blog_image(id):
    """Upload image directly to a blog post"""
    from werkzeug.utils import secure_filename
    import os
    
    post = BlogPost.query.get_or_404(id)
    
    # Check permission
    if current_user.role != 'super_admin' and post.author_id != current_user.id:
        return jsonify({'error': 'You can only upload images to your own blog posts'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Check file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Create blog images folder
    from app import app
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