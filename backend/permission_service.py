from models import db, UserPermission
from flask_login import current_user


ROLE_PERMISSIONS = {
    'super_admin': {
        'products': ['create', 'read', 'update', 'delete'],
        'blog': ['create', 'read', 'update', 'delete', 'publish'],
        'jobs': ['create', 'read', 'update', 'delete'],
        'outlets': ['create', 'read', 'update', 'delete'],
        'users': ['create', 'read', 'update', 'delete'],
        'partners': ['create', 'read', 'update', 'delete'],
        'referrals': ['create', 'read', 'update', 'delete'],
        'statistics': ['read', 'update'],
        
        'contacts': ['read', 'update', 'delete'],
        'uploads': ['create'],
        'permissions': ['read', 'create', 'update', 'delete']
    },
    'admin': {
        'products': ['create', 'read', 'update'],
        'blog': ['create', 'read', 'update'], 
        'jobs': ['create', 'read', 'update'],
        'outlets': ['create', 'read', 'update'],
        'users': ['read'],
        'partners': ['create', 'read', 'update'],
        'referrals': ['create', 'read', 'update'],
        'statistics': ['read'],
        'contacts': ['read', 'update'],
        'uploads': ['create'],
        'permissions': []
    },
    'partner': {
        'products': ['read'],
        'blog': ['read'], 
        'jobs': ['read'],
        'outlets': ['read'],
        'users': [],
        'partners': [],
        'referrals': ['create', 'read', 'update'],
        'contacts': [],
        'uploads': [],
        'permissions': []
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