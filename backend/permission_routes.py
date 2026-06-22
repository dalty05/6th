from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, User, UserPermission
from permission_service import has_permission, get_user_permissions, ROLE_PERMISSIONS
from datetime import datetime












permission_bp = Blueprint('permission', __name__)

@permission_bp.route('/permissions/users/<int:user_id>', methods=['GET'])
@login_required
def get_user_permissions_route(user_id):
    """Get permissions for a specific user"""
    # Only super admin can view other users' permissions
    if current_user.role != 'super_admin' and current_user.id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    user = User.query.get_or_404(user_id)
    
    # Get custom permissions from database
    custom_perms = UserPermission.query.filter_by(user_id=user_id).all()
    
    # Get effective permissions using the same logic as middleware
    resources = ['products', 'blog', 'jobs', 'outlets', 'users', 'partners', 'referrals', 'statistics', 'contacts']
    actions = ['create', 'read', 'update', 'delete']
    
    effective_permissions = {}
    for resource in resources:
        effective_permissions[resource] = {}
        for action in actions:
            effective_permissions[resource][action] = has_permission(user, resource, action)
    
    return jsonify({
        'user': {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'is_active': user.is_active
        },
        'custom_permissions': [{
            'id': p.id,
            'resource': p.resource,
            'action': p.action,
            'is_allowed': p.is_allowed
        } for p in custom_perms],
        'role_defaults': ROLE_PERMISSIONS.get(user.role, {}),
        'effective_permissions': effective_permissions
    }), 200

@permission_bp.route('/permissions/users/<int:user_id>', methods=['POST'])
@login_required
def set_user_permission(user_id):
    """Set a custom permission for a user"""
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
    return jsonify({'message': 'Permission set', 'id': perm.id}), 200

@permission_bp.route('/permissions/users/<int:user_id>/<int:perm_id>', methods=['DELETE'])
@login_required
def delete_user_permission(user_id, perm_id):
    """Delete a custom permission"""
    if current_user.role != 'super_admin':
        return jsonify({'error': 'Super admin only'}), 403
    
    perm = UserPermission.query.get_or_404(perm_id)
    if perm.user_id != user_id:
        return jsonify({'error': 'Permission not found for this user'}), 404
    
    db.session.delete(perm)
    db.session.commit()
    return jsonify({'message': 'Permission removed'}), 200

@permission_bp.route('/permissions/resources', methods=['GET'])
@login_required
def get_resources():
    """Get list of all resources and available actions"""
    if current_user.role != 'super_admin':
        return jsonify({'error': 'Super admin only'}), 403
    
    resources = [
        {'name': 'products', 'label': 'Products', 'actions': ['create', 'read', 'update', 'delete']},
        {'name': 'blog', 'label': 'Blog Posts', 'actions': ['create', 'read', 'update', 'delete']},
        {'name': 'jobs', 'label': 'Jobs', 'actions': ['create', 'read', 'update', 'delete']},
        {'name': 'outlets', 'label': 'Outlets', 'actions': ['create', 'read', 'update', 'delete']},
        {'name': 'users', 'label': 'Users', 'actions': ['create', 'read', 'update', 'delete']},
        {'name': 'partners', 'label': 'Partners', 'actions': ['create', 'read', 'update', 'delete']},
        {'name': 'referrals', 'label': 'Referrals', 'actions': ['create', 'read', 'update', 'delete']},
        {'name': 'statistics', 'label': 'Statistics', 'actions': ['read']},
        {'name': 'contacts', 'label': 'Contacts', 'actions': ['read', 'update', 'delete']}
    ]
    return jsonify(resources), 200

@permission_bp.route('/permissions/check', methods=['POST'])
@login_required
def check_permission():
    """Check if current user has a specific permission"""
    data = request.json
    resource = data.get('resource')
    action = data.get('action')
    
    if not resource or not action:
        return jsonify({'error': 'Resource and action required'}), 400
    
    return jsonify({
        'has_permission': has_permission(current_user, resource, action)
    }), 200