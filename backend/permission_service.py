from models import db, UserPermission
from flask_login import current_user


ROLE_PERMISSIONS = {
    'super_admin': {
        'products': {'create': True, 'read': True, 'update': True, 'delete': True},
        'blog': {'create': True, 'read': True, 'update': True, 'delete': True},
        'jobs': {'create': True, 'read': True, 'update': True, 'delete': True},
        'outlets': {'create': True, 'read': True, 'update': True, 'delete': True},
        'users': {'create': True, 'read': True, 'update': True, 'delete': True},
        'partners': {'create': True, 'read': True, 'update': True, 'delete': True},
        'referrals': {'create': True, 'read': True, 'update': True, 'delete': True},
        'statistics': {'create': True, 'read': True, 'update': True, 'delete': True},
        'contacts': {'create': True, 'read': True, 'update': True, 'delete': True},
        'newsletter': {'create': True, 'read': True, 'update': True, 'delete': True},
        # ========== NEW TOUR PERMISSIONS ==========
        'tours': {'create': True, 'read': True, 'update': True, 'delete': True},
        'bookings': {'create': True, 'read': True, 'update': True, 'delete': True, 'approve': True, 'reject': True},
        'tour_settings': {'create': True, 'read': True, 'update': True, 'delete': True},
    },
    'admin': {
        'products': {'create': True, 'read': True, 'update': True, 'delete': False},
        'blog': {'create': True, 'read': True, 'update': True, 'delete': False},
        'jobs': {'create': True, 'read': True, 'update': True, 'delete': False},
        'outlets': {'create': True, 'read': True, 'update': True, 'delete': False},
        'users': {'create': False, 'read': True, 'update': False, 'delete': False},
        'partners': {'create': True, 'read': True, 'update': True, 'delete': False},
        'referrals': {'create': True, 'read': True, 'update': True, 'delete': False},
        'statistics': {'create': False, 'read': True, 'update': False, 'delete': False},
        'contacts': {'create': False, 'read': True, 'update': True, 'delete': False},
        'newsletter': {'create': True, 'read': True, 'update': True, 'delete': False},
        # ========== NEW TOUR PERMISSIONS ==========
        'tours': {'create': True, 'read': True, 'update': True, 'delete': False},
        'bookings': {'create': True, 'read': True, 'update': True, 'delete': False, 'approve': True, 'reject': True},
        'tour_settings': {'create': False, 'read': True, 'update': False, 'delete': False},
    },
    'tour_manager': {
        # ========== TOUR MANAGER PERMISSIONS ==========
        'tours': {'create': True, 'read': True, 'update': True, 'delete': False},
        'bookings': {'create': False, 'read': True, 'update': True, 'delete': False, 'approve': True, 'reject': True},
        'tour_settings': {'create': False, 'read': True, 'update': False, 'delete': False},
        # Tour managers can view these but not modify
        'statistics': {'create': False, 'read': True, 'update': False, 'delete': False},
        'contacts': {'create': False, 'read': False, 'update': False, 'delete': False},
        'products': {'create': False, 'read': False, 'update': False, 'delete': False},
        'blog': {'create': False, 'read': False, 'update': False, 'delete': False},
        'jobs': {'create': False, 'read': False, 'update': False, 'delete': False},
        'outlets': {'create': False, 'read': False, 'update': False, 'delete': False},
        'users': {'create': False, 'read': False, 'update': False, 'delete': False},
        'partners': {'create': False, 'read': False, 'update': False, 'delete': False},
        'referrals': {'create': False, 'read': False, 'update': False, 'delete': False},
        'newsletter': {'create': False, 'read': False, 'update': False, 'delete': False},
    },
    'tour_assistant': {
        # ========== TOUR ASSISTANT PERMISSIONS ==========
        'tours': {'create': False, 'read': True, 'update': False, 'delete': False},
        'bookings': {'create': False, 'read': True, 'update': True, 'delete': False, 'approve': False, 'reject': False},
        'tour_settings': {'create': False, 'read': True, 'update': False, 'delete': False},
        # Tour assistants can view statistics
        'statistics': {'create': False, 'read': True, 'update': False, 'delete': False},
        # All other resources: no access
        'products': {'create': False, 'read': False, 'update': False, 'delete': False},
        'blog': {'create': False, 'read': False, 'update': False, 'delete': False},
        'jobs': {'create': False, 'read': False, 'update': False, 'delete': False},
        'outlets': {'create': False, 'read': False, 'update': False, 'delete': False},
        'users': {'create': False, 'read': False, 'update': False, 'delete': False},
        'partners': {'create': False, 'read': False, 'update': False, 'delete': False},
        'referrals': {'create': False, 'read': False, 'update': False, 'delete': False},
        'contacts': {'create': False, 'read': False, 'update': False, 'delete': False},
        'newsletter': {'create': False, 'read': False, 'update': False, 'delete': False},
    },
    'partner': {
        'products': {'create': False, 'read': True, 'update': False, 'delete': False},
        'blog': {'create': False, 'read': True, 'update': False, 'delete': False},
        'jobs': {'create': False, 'read': True, 'update': False, 'delete': False},
        'outlets': {'create': False, 'read': True, 'update': False, 'delete': False},
        'users': {'create': False, 'read': False, 'update': False, 'delete': False},
        'partners': {'create': False, 'read': False, 'update': False, 'delete': False},
        'referrals': {'create': True, 'read': True, 'update': True, 'delete': False},
        'statistics': {'create': False, 'read': True, 'update': False, 'delete': False},
        'contacts': {'create': False, 'read': False, 'update': False, 'delete': False},
        'newsletter': {'create': False, 'read': False, 'update': False, 'delete': False},
        # ========== NEW TOUR PERMISSIONS ==========
        'tours': {'create': False, 'read': False, 'update': False, 'delete': False},
        'bookings': {'create': False, 'read': False, 'update': False, 'delete': False, 'approve': False, 'reject': False},
        'tour_settings': {'create': False, 'read': False, 'update': False, 'delete': False},
    }
}


def has_permission(user, resource, action):
    """Check if user has a specific permission"""
    if not user or not user.is_active:
        return False
    
    # Super admin has everything
    if user.role == 'super_admin':
        return True
    
    # Check custom permissions from database
    custom_perm = UserPermission.query.filter_by(
        user_id=user.id,
        resource=resource,
        action=action
    ).first()
    
    if custom_perm is not None:
        return custom_perm.is_allowed
    
    # Fall back to role-based permissions
    allowed_actions = ROLE_PERMISSIONS.get(user.role, {}).get(resource, [])
    return action in allowed_actions

def get_user_permissions(user):
    """Get all permissions for a user as a dictionary"""
    if user.role == 'super_admin':
        return {resource: {action: True for action in actions} 
                for resource, actions in ROLE_PERMISSIONS['super_admin'].items()}
    
    # Get custom permissions
    custom_perms = UserPermission.query.filter_by(user_id=user.id).all()
    custom_map = {(p.resource, p.action): p.is_allowed for p in custom_perms}
    
    # Build full permissions
    permissions = {}
    for resource, allowed_actions in ROLE_PERMISSIONS.get(user.role, {}).items():
        permissions[resource] = {}
        for action in allowed_actions:
            key = (resource, action)
            permissions[resource][action] = custom_map.get(key, True)
    
    return permissions