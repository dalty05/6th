# permission_routes.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, User, PermissionTemplate
import json

permission_bp = Blueprint('permission', __name__)

def role_required(*roles):
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            if current_user.role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@permission_bp.route('/permissions/resources', methods=['GET'])
@login_required
@role_required('super_admin')
def get_resources():
    """Get all available permission resources"""
    resources = [
        {'id': 'products', 'name': 'Products', 'description': 'Manage dairy products', 'actions': ['create', 'read', 'update', 'delete']},
        {'id': 'blog', 'name': 'Blog Posts', 'description': 'Manage blog content', 'actions': ['create', 'read', 'update', 'delete']},
        {'id': 'users', 'name': 'Users', 'description': 'Manage user accounts', 'actions': ['create', 'read', 'update', 'delete']},
        {'id': 'partners', 'name': 'Partners', 'description': 'Manage partner accounts', 'actions': ['create', 'read', 'update', 'delete']},
        {'id': 'referrals', 'name': 'Referrals', 'description': 'Referral links and tracking', 'actions': ['create', 'read', 'update', 'delete']},
        {'id': 'statistics', 'name': 'Statistics', 'description': 'View analytics and reports', 'actions': ['create', 'read', 'update', 'delete']},
        {'id': 'settings', 'name': 'Settings', 'description': 'System configuration', 'actions': ['create', 'read', 'update', 'delete']}
    ]
    return jsonify(resources), 200

@permission_bp.route('/permissions/templates', methods=['GET'])
@login_required
@role_required('super_admin')
def get_templates():
    """Get permission templates for quick assignment"""
    templates = [
        {
            'id': 'partner_full',
            'name': 'Partner - Full Access',
            'description': 'Can create and manage referral links, view all stats'
        },
        {
            'id': 'partner_readonly',
            'name': 'Partner - Read Only',
            'description': 'Can only view stats, cannot create or edit links'
        },
        {
            'id': 'partner_creator',
            'name': 'Partner - Creator',
            'description': 'Can create, edit, and delete own referral links'
        },
        {
            'id': 'admin_full',
            'name': 'Admin - Full Access',
            'description': 'Full product and blog management, can view partners'
        },
        {
            'id': 'admin_limited',
            'name': 'Admin - Limited',
            'description': 'Can edit but not delete products and blog'
        }
    ]
    return jsonify(templates), 200

@permission_bp.route('/users/<int:user_id>/permissions', methods=['GET'])
@login_required
def get_user_permissions(user_id):
    """Get specific user's permissions"""
    user = User.query.get_or_404(user_id)
    
    # Users can only view their own permissions (unless super admin)
    if current_user.id != user_id and current_user.role != 'super_admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(user.get_permissions()), 200

@permission_bp.route('/users/<int:user_id>/permissions', methods=['PUT'])
@login_required
@role_required('super_admin')
def update_user_permissions(user_id):
    """Update user permissions (granular control)"""
    user = User.query.get_or_404(user_id)
    data = request.json
    
    # Don't allow modifying super admin permissions
    if user.role == 'super_admin':
        return jsonify({'error': 'Cannot modify super admin permissions'}), 403
    
    permissions_dict = data.get('permissions', {})
    user.set_permissions_bulk(permissions_dict)
    db.session.commit()
    
    return jsonify({'message': 'Permissions updated successfully'}), 200

@permission_bp.route('/users/<int:user_id>/permissions/<resource>/<action>', methods=['PUT'])
@login_required
@role_required('super_admin')
def toggle_permission(user_id, resource, action):
    """Toggle a single permission for a user"""
    user = User.query.get_or_404(user_id)
    data = request.json
    value = data.get('value', False)
    
    if user.role == 'super_admin':
        return jsonify({'error': 'Cannot modify super admin permissions'}), 403
    
    if action not in ['create', 'read', 'update', 'delete']:
        return jsonify({'error': 'Invalid action'}), 400
    
    user.set_permission(resource, action, value)
    db.session.commit()
    
    return jsonify({'message': f'Permission {resource}.{action} set to {value}'}), 200

@permission_bp.route('/users/<int:user_id>/apply-template', methods=['POST'])
@login_required
@role_required('super_admin')
def apply_permission_template(user_id):
    """Apply a permission template to a user"""
    user = User.query.get_or_404(user_id)
    data = request.json
    template_name = data.get('template')
    
    if user.role == 'super_admin':
        return jsonify({'error': 'Cannot modify super admin permissions'}), 403
    
    template = PermissionTemplate.get_template(template_name)
    if not template:
        return jsonify({'error': 'Invalid template'}), 400
    
    user.set_permissions_bulk(template['permissions'])
    db.session.commit()
    
    return jsonify({'message': f'Template {template_name} applied successfully'}), 200

@permission_bp.route('/users/<int:user_id>/reset-permissions', methods=['POST'])
@login_required
@role_required('super_admin')
def reset_user_permissions(user_id):
    """Reset user permissions to role defaults"""
    user = User.query.get_or_404(user_id)
    
    if user.role == 'super_admin':
        return jsonify({'error': 'Cannot reset super admin permissions'}), 403
    
    # Reset to default permissions for role
    default_perms = user.get_default_permissions()
    user.set_permissions_bulk(default_perms)
    db.session.commit()
    
    return jsonify({'message': 'Permissions reset to default'}), 200