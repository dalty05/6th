from models import db, UserPermission, ResourcePermission
from flask_login import current_user
from services.component_service import ComponentService
from functools import wraps
from flask import jsonify

# ============================================================
# SYSTEM ROLE PERMISSIONS (Hardcoded for system roles)
# ============================================================

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
        'tours': {'create': True, 'read': True, 'update': True, 'delete': True},
        'bookings': {'create': True, 'read': True, 'update': True, 'delete': True, 'approve': True, 'reject': True},
        'tour_settings': {'create': True, 'read': True, 'update': True, 'delete': True},
        'roles': {'create': True, 'read': True, 'update': True, 'delete': True},
        'components': {'create': True, 'read': True, 'update': True, 'delete': True},
        'profile': {'read': True, 'update': True},
        'activities': {'read': True},
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
        'tours': {'create': True, 'read': True, 'update': True, 'delete': False},
        'bookings': {'create': True, 'read': True, 'update': True, 'delete': False, 'approve': True, 'reject': True},
        'tour_settings': {'create': False, 'read': True, 'update': False, 'delete': False},
        'roles': {'create': False, 'read': True, 'update': False, 'delete': False},
        'components': {'create': False, 'read': True, 'update': False, 'delete': False},
        'profile': {'read': True, 'update': True},
        'activities': {'read': True},
    },
    'tour_manager': {
        'tours': {'create': True, 'read': True, 'update': True, 'delete': False},
        'bookings': {'create': False, 'read': True, 'update': True, 'delete': False, 'approve': True, 'reject': True},
        'tour_settings': {'create': False, 'read': True, 'update': False, 'delete': False},
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
        'roles': {'create': False, 'read': False, 'update': False, 'delete': False},
        'components': {'create': False, 'read': False, 'update': False, 'delete': False},
        'profile': {'read': True, 'update': True},
        'activities': {'read': True},
    },
    'tour_assistant': {
        'tours': {'create': False, 'read': True, 'update': False, 'delete': False},
        'bookings': {'create': False, 'read': True, 'update': True, 'delete': False, 'approve': False, 'reject': False},
        'tour_settings': {'create': False, 'read': True, 'update': False, 'delete': False},
        'statistics': {'create': False, 'read': True, 'update': False, 'delete': False},
        'products': {'create': False, 'read': False, 'update': False, 'delete': False},
        'blog': {'create': False, 'read': False, 'update': False, 'delete': False},
        'jobs': {'create': False, 'read': False, 'update': False, 'delete': False},
        'outlets': {'create': False, 'read': False, 'update': False, 'delete': False},
        'users': {'create': False, 'read': False, 'update': False, 'delete': False},
        'partners': {'create': False, 'read': False, 'update': False, 'delete': False},
        'referrals': {'create': False, 'read': False, 'update': False, 'delete': False},
        'contacts': {'create': False, 'read': False, 'update': False, 'delete': False},
        'newsletter': {'create': False, 'read': False, 'update': False, 'delete': False},
        'roles': {'create': False, 'read': False, 'update': False, 'delete': False},
        'components': {'create': False, 'read': False, 'update': False, 'delete': False},
        'profile': {'read': True, 'update': True},
        'activities': {'read': True},
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
        'tours': {'create': False, 'read': False, 'update': False, 'delete': False},
        'bookings': {'create': False, 'read': False, 'update': False, 'delete': False, 'approve': False, 'reject': False},
        'tour_settings': {'create': False, 'read': False, 'update': False, 'delete': False},
        'roles': {'create': False, 'read': False, 'update': False, 'delete': False},
        'components': {'create': False, 'read': False, 'update': False, 'delete': False},
        'profile': {'read': True, 'update': True},
        'activities': {'read': True},
    },
}

# ============================================================
# COMPONENT ACTION MAP
# ============================================================

COMPONENT_ACTION_MAP = {
    'overview': ['read'],
    'products': ['create', 'read', 'update', 'delete'],
    'blog': ['create', 'read', 'update', 'delete'],
    'jobs': ['create', 'read', 'update', 'delete'],
    'outlets': ['create', 'read', 'update', 'delete'],
    'statistics': ['read'],
    'contacts': ['read', 'update', 'delete'],
    'newsletter': ['create', 'read', 'update', 'delete'],
    'users': ['create', 'read', 'update', 'delete'],
    'permissions': ['read', 'update'],
    'roles': ['create', 'read', 'update', 'delete'],
    'components': ['create', 'read', 'update', 'delete'],
    'tours': ['create', 'read', 'update', 'delete'],
    'tour-packages': ['create', 'read', 'update', 'delete'],
    'tour-calendar': ['read', 'update'],
    'tour-payments': ['read', 'update'],
    'tour-reports': ['read'],
    'tour-staff': ['read', 'update'],
    'bookings': ['create', 'read', 'update', 'delete', 'approve', 'reject'],
    'tour_settings': ['read', 'update'],
    'partner-dashboard': ['read'],
    'partner-links': ['create', 'read', 'update', 'delete'],
    'partner-analytics': ['read'],
    'profile': ['read', 'update'],
    'activities': ['read'],
}

# ============================================================
# SYSTEM ROLES LIST
# ============================================================

SYSTEM_ROLES = ['super_admin', 'admin', 'tour_manager', 'tour_assistant', 'partner']

def is_custom_role(role):
    return role not in SYSTEM_ROLES

# ============================================================
# REQUIRE PERMISSION DECORATOR
# ============================================================

def require_permission(resource, action):
    """
    Decorator to check if current user has permission for a resource action.
    Usage: @require_permission('products', 'create')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            
            if not has_permission(current_user, resource, action):
                return jsonify({
                    'error': f'Permission denied: {action} on {resource}',
                    'required': f'{resource}.{action}'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ============================================================
# HAS PERMISSION
# ============================================================

def has_permission(user, resource, action, resource_id=None):
    """
    UNIFIED PERMISSION CHECK - Priority order:
    1. Super admin → always True
    2. Individual custom permission (UserPermission) - HIGHEST PRIORITY
    3. Component-based permissions (from assigned components) - FOR ALL ROLES
    4. System role permissions (from ROLE_PERMISSIONS)
    5. Resource-specific permission (ResourcePermission)
    6. Default deny
    """
    if not user or not user.is_active:
        return False
    
    # 1. Super admin override
    if user.role == 'super_admin':
        return True
    
    # 2. INDIVIDUAL CUSTOM PERMISSION
    try:
        up = UserPermission.query.filter_by(
            user_id=user.id,
            resource=resource,
            action=action
        ).first()
        if up:
            return up.is_allowed
    except Exception as e:
        return False
    
    # 3. COMPONENT-BASED PERMISSIONS
    if ComponentService.user_can_access_component(resource, user.id):
        allowed_actions = COMPONENT_ACTION_MAP.get(resource, ['read'])
        result = action in allowed_actions
        if result:
            return result
    
    # 4. SYSTEM ROLE PERMISSIONS
    if user.role in SYSTEM_ROLES:
        role_perms = ROLE_PERMISSIONS.get(user.role, {})
        result = role_perms.get(resource, {}).get(action, False)
        if result:
            return result
    
    # 5. RESOURCE-SPECIFIC PERMISSION
    if resource_id is not None:
        try:
            rp = ResourcePermission.query.filter_by(
                user_id=user.id,
                resource_type=resource,
                resource_id=resource_id,
                action=action
            ).first()
            if rp:
                return rp.is_allowed
        except:
            pass
    
    return False

# GET USER PERMISSIONS

def get_user_permissions(user):
    """
    Get all permissions for a user as a dictionary.
    """
    if not user:
        return {}
    
    if user.role == 'super_admin':
        return {resource: {action: True for action in actions} 
                for resource, actions in COMPONENT_ACTION_MAP.items()}
    
    permissions = {}
    
    # Custom role
    if user.role not in SYSTEM_ROLES:
        component_keys = []
        
        if hasattr(user, 'role_id') and user.role_id:
            try:
                from models import RoleComponent, DashboardComponent
                role_components = RoleComponent.query.filter_by(
                    role_id=user.role_id
                ).join(DashboardComponent).all()
                for rc in role_components:
                    if rc.component:
                        component_keys.append(rc.component.key)
            except Exception as e:
                print(f"{e}")
        
        if not component_keys:
            try:
                from models import Role
                role_obj = Role.query.filter_by(name=user.role).first()
                if role_obj:
                    role_components = RoleComponent.query.filter_by(
                        role_id=role_obj.id
                    ).join(DashboardComponent).all()
                    for rc in role_components:
                        if rc.component:
                            component_keys.append(rc.component.key)
            except Exception as e:
                print(f"{e}")
        
        for key in component_keys:
            actions = COMPONENT_ACTION_MAP.get(key, ['read'])
            permissions[key] = {action: True for action in actions}
        
        try:
            custom_perms = UserPermission.query.filter_by(user_id=user.id).all()
            for cp in custom_perms:
                if cp.resource not in permissions:
                    permissions[cp.resource] = {}
                permissions[cp.resource][cp.action] = cp.is_allowed
        except Exception as e:
            print(f"Error applying custom permissions: {e}")
        
        return permissions
    
    # System role
    if user.role in SYSTEM_ROLES:
        permissions = ROLE_PERMISSIONS.get(user.role, {}).copy()
    
    try:
        custom_perms = UserPermission.query.filter_by(user_id=user.id).all()
        for cp in custom_perms:
            if cp.resource not in permissions:
                permissions[cp.resource] = {}
            permissions[cp.resource][cp.action] = cp.is_allowed
    except Exception as e:
        print(f"Error applying custom permissions: {e}")
    
    return permissions

# ============================================================
# GET RESOURCE USERS
# ============================================================

def get_resource_users(resource_type, resource_id, action='read'):
    from models import User
    
    super_admins = User.query.filter_by(role='super_admin', is_active=True).all()
    resource_perms = ResourcePermission.query.filter_by(
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        is_allowed=True
    ).all()
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

def is_system_role(role_name):
    return role_name in SYSTEM_ROLES