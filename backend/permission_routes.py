# backend/permission_routes.py

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, User, UserPermission, Role, DashboardComponent, RoleComponent
from permission_service import has_permission, get_user_permissions, ROLE_PERMISSIONS, SYSTEM_ROLES, COMPONENT_ACTION_MAP
from datetime import datetime
from services.activity_logger import log_activity
from functools import wraps

permission_bp = Blueprint('permission', __name__)

# ============================================================
# HELPER: Require permission decorator
# ============================================================

def require_permission(resource, action):
    """Decorator to check if current user has permission for a resource action"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            
            if not has_permission(current_user, resource, action):
                return jsonify({
                    'error': f'Permission denied: {resource}:{action}',
                    'required': f'{resource}.{action}'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============================================================
# GET MY PERMISSIONS - ✅ ANY AUTHENTICATED USER
# ============================================================

@permission_bp.route('/permissions/me', methods=['GET'])
@login_required
def get_my_permissions():
    """
    Get current user's permissions - accessible to ANY authenticated user.
    This endpoint does NOT check for super admin.
    """
    try:
        print(f"🔍 Getting permissions for user: {current_user.email} (role: {current_user.role})")
        
        # Get user's permissions
        permissions = get_user_permissions(current_user)
        
        # Get user's role details
        role_name = current_user.role
        role_display = current_user.role.capitalize() if current_user.role else 'User'
        
        # Get custom permissions count
        custom_perms_count = UserPermission.query.filter_by(user_id=current_user.id).count()
        
        response_data = {
            'permissions': permissions,
            'role': current_user.role,
            'role_name': role_name,
            'role_display': role_display,
            'user_id': current_user.id,
            'email': current_user.email,
            'full_name': current_user.full_name,
            'is_super_admin': current_user.is_super_admin(),
            'is_tour_manager': current_user.is_tour_manager,
            'is_tour_assistant': current_user.is_tour_assistant,
            'custom_permissions_count': custom_perms_count,
            'is_authenticated': True
        }
        
        print(f"✅ Permissions retrieved for {current_user.email}")
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ Error getting permissions: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500





# GET RESOURCES - Requires permissions.read
# ============================================================

@permission_bp.route('/permissions/resources', methods=['GET'])
@login_required
@require_permission('permissions', 'read')
def get_resources():
    """
    Get all available resources and their actions dynamically.
    This includes resources from DashboardComponent and COMPONENT_ACTION_MAP.
    """
    resources_dict = {}
    
    # 1. Get resources from DashboardComponent
    try:
        components = DashboardComponent.query.filter_by(is_active=True).all()
        for comp in components:
            key = comp.key
            if key not in resources_dict:
                actions = COMPONENT_ACTION_MAP.get(key, ['read'])
                resources_dict[key] = {
                    'name': key,
                    'label': comp.label,
                    'actions': actions,
                    'component_id': comp.id,
                    'is_active': comp.is_active
                }
    except Exception as e:
        print(f"Error loading components from database: {e}")
    
    # 2. Get resources from COMPONENT_ACTION_MAP that aren't in database
    for key, actions in COMPONENT_ACTION_MAP.items():
        if key not in resources_dict:
            comp = DashboardComponent.query.filter_by(key=key).first()
            if comp:
                resources_dict[key] = {
                    'name': key,
                    'label': comp.label,
                    'actions': actions,
                    'component_id': comp.id,
                    'is_active': comp.is_active
                }
            else:
                resources_dict[key] = {
                    'name': key,
                    'label': key.replace('_', ' ').title(),
                    'actions': actions,
                    'component_id': None,
                    'is_active': True
                }
    
    # 3. Convert to list and sort
    resources = list(resources_dict.values())
    resources.sort(key=lambda x: x['label'])
    
    return jsonify(resources), 200

# ============================================================
# GET USER PERMISSIONS - Requires users.read AND permissions.read
# ============================================================

@permission_bp.route('/permissions/users/<int:user_id>', methods=['GET'])
@login_required
@require_permission('users', 'read')
@require_permission('permissions', 'read')
def get_user_permissions_route(user_id):
    """Get permissions for a specific user"""
    if current_user.id != user_id and not current_user.is_super_admin():
        return jsonify({'error': 'Permission denied'}), 403
    
    user = User.query.get_or_404(user_id)
    
    custom_perms = UserPermission.query.filter_by(user_id=user_id).all()
    
    # Get dynamic resources
    components = DashboardComponent.query.filter_by(is_active=True).all()
    resources = [comp.key for comp in components]
    for key in COMPONENT_ACTION_MAP.keys():
        if key not in resources:
            resources.append(key)
    
    actions = ['create', 'read', 'update', 'delete', 'approve', 'reject']
    
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
        'role_defaults': ROLE_PERMISSIONS.get(user.role, {}),
        'effective_permissions': effective_permissions
    }), 200

# ============================================================
# SET USER PERMISSION - Requires permissions.update
# ============================================================

@permission_bp.route('/permissions/users/<int:user_id>', methods=['POST'])
@login_required
@require_permission('permissions', 'update')
def set_user_permission(user_id):
    """Set a custom permission for a user"""
    if not current_user.is_super_admin():
        return jsonify({'error': 'Super admin only'}), 403
    
    data = request.json
    resource = data.get('resource')
    action = data.get('action')
    is_allowed = data.get('is_allowed', True)
    
    if not resource or not action:
        return jsonify({'error': 'Resource and action required'}), 400
    
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
        current_user, 
        'update', 
        'permissions', 
        user_id, 
        f'Set {resource}:{action} to {is_allowed} for user {user_id}'
    )
    
    return jsonify({'message': 'Permission set', 'id': perm.id}), 200

# ============================================================
# DELETE USER PERMISSION - Requires permissions.delete
# ============================================================

@permission_bp.route('/permissions/users/<int:user_id>/<int:perm_id>', methods=['DELETE'])
@login_required
@require_permission('permissions', 'delete')
def delete_user_permission(user_id, perm_id):
    """Delete a custom permission"""
    if not current_user.is_super_admin():
        return jsonify({'error': 'Super admin only'}), 403
    
    perm = UserPermission.query.get_or_404(perm_id)
    if perm.user_id != user_id:
        return jsonify({'error': 'Permission not found for this user'}), 404
    
    db.session.delete(perm)
    db.session.commit()
    
    log_activity(
        current_user, 
        'delete', 
        'permissions', 
        user_id, 
        f'Deleted permission for user {user_id}'
    )
    
    return jsonify({'message': 'Permission removed'}), 200

# ============================================================
# PERMISSION CHECK - Public check endpoint
# ============================================================

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

# ============================================================
# DASHBOARD CONFIG - Shows components based on permissions
# ============================================================










@permission_bp.route('/dashboard/config', methods=['GET'])
@login_required
def get_dashboard_config():
    """Get dashboard configuration for current user"""
    try:
        user = current_user
        
        if user.is_super_admin():
            components = DashboardComponent.query.filter_by(is_active=True).order_by(
                DashboardComponent.order
            ).all()
        elif user.role in SYSTEM_ROLES:
            role_perms = ROLE_PERMISSIONS.get(user.role, {})
            component_keys = [key for key, perms in role_perms.items() 
                             if perms.get('read', False)]
            components = DashboardComponent.query.filter(
                DashboardComponent.key.in_(component_keys),
                DashboardComponent.is_active == True
            ).order_by(DashboardComponent.order).all()
        else:
            if user.role_id:
                role_components = RoleComponent.query.filter_by(
                    role_id=user.role_id
                ).join(DashboardComponent).filter(
                    DashboardComponent.is_active == True
                ).order_by(DashboardComponent.order).all()
                components = [rc.component for rc in role_components]
            else:
                components = []
        
        return jsonify({
            'components': [c.to_dict() for c in components],
            'role': {
                'id': user.role_id,
                'name': user.role,
                'display_name': user.role.capitalize()
            }
        }), 200
        
    except Exception as e:
        print(f"Error in dashboard config: {e}")
        return jsonify({'error': str(e)}), 500
    

@permission_bp.route('/roles', methods=['POST'])
@login_required
@require_permission('roles', 'create')
def create_role():
    """Create a new role with optional template"""
    if not current_user.is_super_admin():
        return jsonify({'error': 'Super admin only'}), 403
    
    data = request.json
    name = data.get('name')
    description = data.get('description')
    template = data.get('template', 'admin')  # ✅ Default to admin template
    component_ids = data.get('component_ids', [])
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    if Role.query.filter_by(name=name).first():
        return jsonify({'error': 'Role already exists'}), 400
    
    # ✅ If no components provided, use template
    if not component_ids and template:
        # Get components from template role
        template_role = None
        
        if template == 'admin':
            template_role = Role.query.filter_by(name='admin').first()
        elif template == 'tour_manager':
            template_role = Role.query.filter_by(name='tour_manager').first()
        elif template == 'partner':
            template_role = Role.query.filter_by(name='partner').first()
        
        if template_role:
            # Copy components from template
            for rc in template_role.components:
                component_ids.append(rc.component_id)
    
    # Create the role
    role = Role(
        name=name,
        description=description or f'Custom role based on {template}',
        is_system=False,
        created_by_id=current_user.id,
        is_active=True
    )
    db.session.add(role)
    db.session.commit()
    
    # Add components to the role
    for comp_id in component_ids:
        comp = DashboardComponent.query.get(comp_id)
        if comp:
            role_component = RoleComponent(
                role_id=role.id,
                component_id=comp_id
            )
            db.session.add(role_component)
    
    db.session.commit()
    
    log_activity(
        current_user,
        'create',
        'roles',
        role.id,
        f'Created role {name} with {len(component_ids)} components (template: {template})'
    )
    
    return jsonify({
        'message': 'Role created successfully',
        'role': role.to_dict(),
        'template_used': template
    }), 201


@permission_bp.route('/roles/<int:role_id>/copy', methods=['POST'])
@login_required
@require_permission('roles', 'create')
def copy_role(role_id):
    """Copy permissions from an existing role to a new role"""
    if not current_user.is_super_admin():
        return jsonify({'error': 'Super admin only'}), 403
    
    data = request.json
    new_name = data.get('name')
    new_description = data.get('description')
    
    if not new_name:
        return jsonify({'error': 'New role name is required'}), 400
    
    # Get source role
    source_role = Role.query.get_or_404(role_id)
    
    # Check if new role name exists
    if Role.query.filter_by(name=new_name).first():
        return jsonify({'error': 'Role name already exists'}), 400
    
    # Create new role
    new_role = Role(
        name=new_name,
        description=new_description or f'Copy of {source_role.name}',
        is_system=False,
        created_by_id=current_user.id,
        is_active=True
    )
    db.session.add(new_role)
    db.session.commit()
    
    # Copy components from source role
    for rc in source_role.components:
        role_component = RoleComponent(
            role_id=new_role.id,
            component_id=rc.component_id
        )
        db.session.add(role_component)
    
    db.session.commit()
    
    log_activity(
        current_user,
        'create',
        'roles',
        new_role.id,
        f'Created role {new_name} by copying {source_role.name}'
    )
    
    return jsonify({
        'message': f'Role copied successfully from {source_role.name}',
        'role': new_role.to_dict()
    }), 201





