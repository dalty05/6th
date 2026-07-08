# backend/permission_service.py

from models import db, UserPermission, ResourcePermission
from flask_login import current_user

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
# COMPONENT ACTION MAP - Defines what actions each component supports
# ============================================================

COMPONENT_ACTION_MAP = {
    # Core Components
    'overview': ['read'],
    'products': ['create', 'read', 'update', 'delete'],
    'blog': ['create', 'read', 'update', 'delete'],
    'jobs': ['create', 'read', 'update', 'delete'],
    'outlets': ['create', 'read', 'update', 'delete'],
    'statistics': ['read'],
    'contacts': ['read', 'update', 'delete'],
    'newsletter': ['create', 'read', 'update', 'delete'],
    
    # Administration
    'users': ['create', 'read', 'update', 'delete'],
    'permissions': ['read', 'update'],
    'roles': ['create', 'read', 'update', 'delete'],
    'components': ['create', 'read', 'update', 'delete'],
    
    # Tour Management
    'tours': ['create', 'read', 'update', 'delete'],
    'tour-packages': ['create', 'read', 'update', 'delete'],
    'tour-calendar': ['read', 'update'],
    'tour-payments': ['read', 'update'],
    'tour-reports': ['read'],
    'tour-staff': ['read', 'update'],
    'bookings': ['create', 'read', 'update', 'delete', 'approve', 'reject'],
    'tour_settings': ['read', 'update'],
    
    # Partner
    'partner-dashboard': ['read'],
    'partner-links': ['create', 'read', 'update', 'delete'],
    'partner-analytics': ['read'],

    # Profile
    'profile': ['read', 'update'],
    'activities': ['read'],
}


# ============================================================
# SYSTEM ROLES LIST
# ============================================================

SYSTEM_ROLES = ['super_admin', 'admin', 'tour_manager', 'tour_assistant', 'partner']
def is_custom_role(role):
    """Check if a role is a custom role (not a system role)"""
    return role not in SYSTEM_ROLES

# HAS PERMISSION 


def has_permission(user, resource, action, resource_id=None):
    """
    UNIFIED PERMISSION CHECK - Priority order:
    1. Super admin → always True
    2. Individual custom permission (UserPermission) - HIGHEST PRIORITY
    3. Component-based permissions (from assigned components) - ✅ FOR CUSTOM ROLES
    4. System role permissions (from ROLE_PERMISSIONS)
    5. Resource-specific permission (ResourcePermission)
    6. Default deny
    """
    if not user or not user.is_active:
        return False
    
    # 1. Super admin override
    if user.role == 'super_admin':
        return True
    
    # 2. INDIVIDUAL CUSTOM PERMISSION (Highest priority)
    try:
        up = UserPermission.query.filter_by(
            user_id=user.id,
            resource=resource,
            action=action
        ).first()
        if up:
            print(f"🔍 Individual custom permission: {user.email} -> {resource}.{action} = {up.is_allowed}")
            return up.is_allowed
    except Exception as e:
        print(f"Error checking UserPermission: {e}")
    
    # ✅ 3. CHECK IF USER HAS A CUSTOM ROLE (NOT IN SYSTEM_ROLES)
    if user.role not in SYSTEM_ROLES:
        # This is a custom role - check component-based permissions
        print(f"🔍 Checking custom role: {user.role}")
        
        if hasattr(user, 'role_id') and user.role_id:
            try:
                from models import RoleComponent, DashboardComponent
                
                # Get all components assigned to this role
                role_components = RoleComponent.query.filter_by(
                    role_id=user.role_id
                ).join(DashboardComponent).all()
                
                component_keys = [rc.component.key for rc in role_components]
                print(f"🔍 Custom role components: {component_keys}")
                
                # Check if the resource is in the component list
                if resource in component_keys:
                    allowed_actions = COMPONENT_ACTION_MAP.get(resource, ['read'])
                    result = action in allowed_actions
                    print(f"🔍 Custom role permission: {user.role} -> {resource}.{action} = {result}")
                    return result
                
                # Check for sub-resources (e.g., 'tour-packages' is part of 'tours')
                for rc in role_components:
                    comp = rc.component
                    if comp and resource.startswith(comp.key):
                        allowed_actions = COMPONENT_ACTION_MAP.get(comp.key, ['read'])
                        result = action in allowed_actions
                        print(f"🔍 Custom role (sub-resource): {user.role} -> {resource}.{action} = {result}")
                        return result
                        
            except Exception as e:
                print(f"Error in component-based check: {e}")
        
        # If no role_id or no components found, check by role name in database
        try:
            from models import Role
            role_obj = Role.query.filter_by(name=user.role).first()
            if role_obj:
                role_components = RoleComponent.query.filter_by(
                    role_id=role_obj.id
                ).join(DashboardComponent).all()
                
                component_keys = [rc.component.key for rc in role_components]
                if resource in component_keys:
                    allowed_actions = COMPONENT_ACTION_MAP.get(resource, ['read'])
                    result = action in allowed_actions
                    print(f"🔍 Custom role (by name): {user.role} -> {resource}.{action} = {result}")
                    return result
        except Exception as e:
            print(f"Error in role name check: {e}")
        
        # ✅ For custom roles, also check individual permissions as fallback
        try:
            custom_perms = UserPermission.query.filter_by(user_id=user.id).all()
            for cp in custom_perms:
                if cp.resource == resource and cp.action == action:
                    print(f"🔍 Individual custom permission (fallback): {user.email} -> {resource}.{action} = {cp.is_allowed}")
                    return cp.is_allowed
        except Exception as e:
            print(f"Error in fallback permission check: {e}")
    
    # 4. SYSTEM ROLE PERMISSIONS (Only for system roles)
    if user.role in SYSTEM_ROLES:
        role_perms = ROLE_PERMISSIONS.get(user.role, {})
        result = role_perms.get(resource, {}).get(action, False)
        print(f"🔍 System role: {user.role} -> {resource}.{action} = {result}")
        return result
    
    # 5. RESOURCE-SPECIFIC PERMISSION (if resource_id provided)
    if resource_id is not None:
        try:
            rp = ResourcePermission.query.filter_by(
                user_id=user.id,
                resource_type=resource,
                resource_id=resource_id,
                action=action
            ).first()
            if rp:
                print(f"🔍 Resource-specific: {user.email} -> {resource}.{action} = {rp.is_allowed}")
                return rp.is_allowed
        except:
            pass
    
    # 6. Default deny
    print(f"❌ No permission found: {user.email} -> {resource}.{action} (role: {user.role})")
    return False




# ============================================================
# GET USER PERMISSIONS - For frontend
# ============================================================



def get_user_permissions(user):
    """
    Get all permissions for a user as a dictionary.
    This is used by the frontend /debug/permissions endpoint.
    """
    if not user:
        return {}
    
    # Super admin gets everything
    if user.role == 'super_admin':
        return {resource: {action: True for action in actions} 
                for resource, actions in COMPONENT_ACTION_MAP.items()}
    
    permissions = {}
    
    # ✅ 1. Check if user has a custom role
    if user.role not in SYSTEM_ROLES:
        # Custom role - get permissions from assigned components
        component_keys = []
        
        if hasattr(user, 'role_id') and user.role_id:
            try:
                from models import RoleComponent, DashboardComponent
                
                role_components = RoleComponent.query.filter_by(
                    role_id=user.role_id
                ).join(DashboardComponent).all()
                
                for rc in role_components:
                    comp = rc.component
                    if comp:
                        component_keys.append(comp.key)
            except Exception as e:
                print(f"Error getting custom role permissions: {e}")
        
        # If no role_id, try by role name
        if not component_keys:
            try:
                from models import Role
                role_obj = Role.query.filter_by(name=user.role).first()
                if role_obj:
                    role_components = RoleComponent.query.filter_by(
                        role_id=role_obj.id
                    ).join(DashboardComponent).all()
                    
                    for rc in role_components:
                        comp = rc.component
                        if comp:
                            component_keys.append(comp.key)
            except Exception as e:
                print(f"Error getting role by name: {e}")
        
        # Build permissions from component keys
        for key in component_keys:
            actions = COMPONENT_ACTION_MAP.get(key, ['read'])
            permissions[key] = {action: True for action in actions}
        
        # Apply individual custom permissions
        try:
            custom_perms = UserPermission.query.filter_by(user_id=user.id).all()
            for cp in custom_perms:
                if cp.resource not in permissions:
                    permissions[cp.resource] = {}
                permissions[cp.resource][cp.action] = cp.is_allowed
        except Exception as e:
            print(f"Error applying custom permissions: {e}")
        
        return permissions
    
    # 2. System role permissions
    if user.role in SYSTEM_ROLES:
        permissions = ROLE_PERMISSIONS.get(user.role, {}).copy()
    
    # 3. Apply individual custom permissions (overrides)
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
    """Get list of users who have access to a specific resource"""
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
    """Check if a role is a system role"""
    return role_name in SYSTEM_ROLES