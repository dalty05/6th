# backend/services/permission_service.py
from models import db, UserPermission, ResourcePermission, User
from flask_login import current_user
from functools import wraps
from flask import jsonify

# Default role-based permissions
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
        'contacts': {'create': True, 'read': True, 'update': True, 'delete': True}
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
        'contacts': {'create': False, 'read': True, 'update': True, 'delete': False}
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
        'contacts': {'create': False, 'read': False, 'update': False, 'delete': False}
    }
}



def can_access(user, resource_type, action, resource_id=None):
    """
    Check permission in priority order:
    1. Super admin → always True
    2. Resource-specific permission (if resource_id provided)
    3. User-specific custom permission
    4. Role-based default permission
    5. Default deny
    """
    if not user or not user.is_active:
        return False
    
    # 1. Super admin override
    if user.role == 'super_admin':
        return True
    
    # 2. Resource-level permission (specific item)
    if resource_id is not None:
        rp = ResourcePermission.query.filter_by(
            user_id=user.id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action
        ).first()
        if rp:
            return rp.is_allowed
    
    # 3. User-specific custom permission (overrides role)
    up = UserPermission.query.filter_by(
        user_id=user.id,
        resource=resource_type,
        action=action
    ).first()
    if up:
        return up.is_allowed
    
    # 4. Role-based default
    role_perms = ROLE_PERMISSIONS.get(user.role, {})
    return role_perms.get(resource_type, {}).get(action, False)



def get_user_permissions(user):
    """Get complete permission summary for a user"""
    if user.role == 'super_admin':
        return {'role': 'super_admin', 'permissions': 'full_access'}
    
    # Start with role defaults
    permissions = ROLE_PERMISSIONS.get(user.role, {}).copy()
    
    # Apply custom overrides
    custom_perms = UserPermission.query.filter_by(user_id=user.id).all()
    for cp in custom_perms:
        if cp.resource not in permissions:
            permissions[cp.resource] = {}
        permissions[cp.resource][cp.action] = cp.is_allowed
    
    return {
        'role': user.role,
        'permissions': permissions,
        'has_custom_overrides': len(custom_perms) > 0
    }

def get_resource_users(resource_type, resource_id, action='read'):
    """Get list of users who have access to a specific resource"""
    # Super admins always have access
    super_admins = User.query.filter_by(role='super_admin', is_active=True).all()
    
    # Users with resource-specific permissions
    resource_perms = ResourcePermission.query.filter_by(
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        is_allowed=True
    ).all()
    
    # Users with global permissions for this resource type
    global_perms = UserPermission.query.filter_by(
        resource=resource_type,
        action=action,
        is_allowed=True
    ).all()
    
    users = set()
    for sa in super_admins:
        users.add(sa)
    for rp in resource_perms:
        users.add(rp.user)
    for gp in global_perms:
        users.add(gp.user)
    
    return list(users)# backend/services/permission_service.py
from models import db, UserPermission, ResourcePermission, User
from flask_login import current_user
from functools import wraps
from flask import jsonify

# Default role-based permissions
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
        'contacts': {'create': True, 'read': True, 'update': True, 'delete': True}
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
        'contacts': {'create': False, 'read': True, 'update': True, 'delete': False}
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
        'contacts': {'create': False, 'read': False, 'update': False, 'delete': False}
    }
}

def can_access(user, resource_type, action, resource_id=None):
    """
    Check permission in priority order:
    1. Super admin → always True
    2. Resource-specific permission (if resource_id provided)
    3. User-specific custom permission
    4. Role-based default permission
    5. Default deny
    """
    if not user or not user.is_active:
        return False
    
    # 1. Super admin override
    if user.role == 'super_admin':
        return True
    
    # 2. Resource-level permission (specific item)
    if resource_id is not None:
        rp = ResourcePermission.query.filter_by(
            user_id=user.id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action
        ).first()
        if rp:
            return rp.is_allowed
    
    # 3. User-specific custom permission (overrides role)
    up = UserPermission.query.filter_by(
        user_id=user.id,
        resource=resource_type,
        action=action
    ).first()
    if up:
        return up.is_allowed
    
    # 4. Role-based default
    role_perms = ROLE_PERMISSIONS.get(user.role, {})
    return role_perms.get(resource_type, {}).get(action, False)

def get_user_permissions(user):
    """Get complete permission summary for a user"""
    if user.role == 'super_admin':
        return {'role': 'super_admin', 'permissions': 'full_access'}
    
    # Start with role defaults
    permissions = ROLE_PERMISSIONS.get(user.role, {}).copy()
    
    # Apply custom overrides
    custom_perms = UserPermission.query.filter_by(user_id=user.id).all()
    for cp in custom_perms:
        if cp.resource not in permissions:
            permissions[cp.resource] = {}
        permissions[cp.resource][cp.action] = cp.is_allowed
    
    return {
        'role': user.role,
        'permissions': permissions,
        'has_custom_overrides': len(custom_perms) > 0
    }

def get_resource_users(resource_type, resource_id, action='read'):
    """Get list of users who have access to a specific resource"""
    # Super admins always have access
    super_admins = User.query.filter_by(role='super_admin', is_active=True).all()
    
    # Users with resource-specific permissions
    resource_perms = ResourcePermission.query.filter_by(
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        is_allowed=True
    ).all()
    
    # Users with global permissions for this resource type
    global_perms = UserPermission.query.filter_by(
        resource=resource_type,
        action=action,
        is_allowed=True
    ).all()
    
    users = set()
    for sa in super_admins:
        users.add(sa)
    for rp in resource_perms:
        users.add(rp.user)
    for gp in global_perms:
        users.add(gp.user)
    
    return list(users)