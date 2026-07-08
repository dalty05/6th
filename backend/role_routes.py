# backend/role_routes.py

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Role, DashboardComponent, RoleComponent, User
from permission_service import has_permission, get_user_permissions, ROLE_PERMISSIONS, SYSTEM_ROLES  
from services.component_registry import ComponentRegistry
from datetime import datetime
from functools import wraps

role_bp = Blueprint('role', __name__, url_prefix='/api')


# ============ CUSTOM PERMISSION DECORATOR ============




def require_permission(resource, action):
    """
    Custom decorator to check permissions using has_permission
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            
            if not has_permission(current_user, resource, action):
                return jsonify({
                    'error': f'Permission denied: {action} on {resource}'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator




# ============ ROLE CRUD ============

@role_bp.route('/roles', methods=['GET'])
@login_required
@require_permission('roles', 'read')
def get_roles():
    """Get all roles with their component counts"""
    try:
        roles = Role.query.order_by(Role.is_system.desc(), Role.name).all()
        return jsonify([r.to_dict() for r in roles]), 200
    except Exception as e:
        current_app.logger.error(f"Error getting roles: {str(e)}")
        return jsonify({'error': str(e)}), 500


@role_bp.route('/roles', methods=['POST'])
@login_required
@require_permission('roles', 'create')
def create_role():
    """Create a new role"""
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Role name is required'}), 400
        
        # Check if role exists
        existing = Role.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': 'Role already exists'}), 400
        
        role = Role(
            name=data['name'],
            description=data.get('description', ''),
            is_system=False,
            is_active=data.get('is_active', True),
            created_by_id=current_user.id
        )
        
        db.session.add(role)
        db.session.commit()
        
        # Refresh component registry
        ComponentRegistry.refresh()
        
        return jsonify(role.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating role: {str(e)}")
        return jsonify({'error': str(e)}), 500


@role_bp.route('/roles/<int:role_id>', methods=['PUT'])
@login_required
@require_permission('roles', 'update')
def update_role(role_id):
    """Update a role"""
    try:
        role = Role.query.get_or_404(role_id)
        
        if role.is_system:
            return jsonify({'error': 'Cannot modify system role'}), 400
        
        data = request.get_json()
        
        if 'name' in data:
            existing = Role.query.filter(Role.name == data['name'], Role.id != role_id).first()
            if existing:
                return jsonify({'error': 'Role name already taken'}), 400
            role.name = data['name']
        
        if 'description' in data:
            role.description = data['description']
        
        if 'is_active' in data:
            role.is_active = data['is_active']
        
        role.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Refresh component registry
        ComponentRegistry.refresh()
        
        return jsonify(role.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating role: {str(e)}")
        return jsonify({'error': str(e)}), 500


@role_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@login_required
@require_permission('roles', 'delete')
def delete_role(role_id):
    """Delete a role"""
    try:
        role = Role.query.get_or_404(role_id)
        
        if role.is_system:
            return jsonify({'error': 'Cannot delete system role'}), 400
        
        # Check if users are assigned
        user_count = User.query.filter_by(role_id=role_id).count()
        if user_count > 0:
            return jsonify({
                'error': f'Cannot delete role with {user_count} assigned users. Reassign users first.'
            }), 400
        
        db.session.delete(role)
        db.session.commit()
        
        # Refresh component registry
        ComponentRegistry.refresh()
        
        return jsonify({'message': 'Role deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting role: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============ ROLE-COMPONENT ASSIGNMENT ============

@role_bp.route('/roles/<int:role_id>/components', methods=['GET'])
@login_required
@require_permission('roles', 'read')
def get_role_components(role_id):
    """Get components assigned to a role"""
    try:
        role = Role.query.get_or_404(role_id)
        return jsonify([rc.to_dict() for rc in role.components]), 200
    except Exception as e:
        current_app.logger.error(f"Error getting role components: {str(e)}")
        return jsonify({'error': str(e)}), 500

@role_bp.route('/roles/<int:role_id>/components', methods=['PUT'])
@login_required
@require_permission('roles', 'update')
def assign_role_components(role_id):
    """Assign components to a role"""
    try:
        role = Role.query.get_or_404(role_id)
        
        if role.is_system:
            return jsonify({'error': 'Cannot modify system role'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # ✅ Get component_ids from request
        component_ids = data.get('component_ids', [])
        
        if not isinstance(component_ids, list):
            return jsonify({'error': 'component_ids must be a list'}), 400
        
        # Clear existing assignments
        RoleComponent.query.filter_by(role_id=role_id).delete()
        
        # Add new assignments
        for idx, comp_id in enumerate(component_ids):
            # Verify component exists
            comp = DashboardComponent.query.get(comp_id)
            if not comp:
                return jsonify({'error': f'Component {comp_id} not found'}), 404
            
            rc = RoleComponent(
                role_id=role_id,
                component_id=comp_id,
                order=idx
            )
            db.session.add(rc)
        
        db.session.commit()
        
        # Refresh component registry
        ComponentRegistry.refresh()
        
        return jsonify({
            'message': f'Assigned {len(component_ids)} components to {role.name}',
            'component_count': len(component_ids)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error assigning components: {str(e)}")
        return jsonify({'error': str(e)}), 500



# ============ COMPONENT MANAGEMENT ============

@role_bp.route('/components', methods=['GET'])
@login_required
def get_components():
    """Get all available dashboard components"""
    try:
        components = DashboardComponent.query.filter_by(is_active=True).order_by(
            DashboardComponent.section, DashboardComponent.order
        ).all()
        return jsonify([c.to_dict() for c in components]), 200
    except Exception as e:
        current_app.logger.error(f"Error getting components: {str(e)}")
        return jsonify({'error': str(e)}), 500


@role_bp.route('/components', methods=['POST'])
@login_required
@require_permission('components', 'create')
def create_component():
    """Create a new dashboard component"""
    try:
        data = request.get_json()
        
        required = ['key', 'label', 'component_name']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if component exists
        existing = DashboardComponent.query.filter_by(key=data['key']).first()
        if existing:
            return jsonify({'error': 'Component with this key already exists'}), 400
        
        component = DashboardComponent(
            key=data['key'],
            label=data['label'],
            icon=data.get('icon', 'fas fa-cube'),
            component_name=data['component_name'],
            path=data.get('path', f"/admin/{data['key']}"),
            description=data.get('description', ''),
            section=data.get('section', 'Main'),
            order=data.get('order', 0),
            required_permissions=data.get('required_permissions', [])
        )
        
        db.session.add(component)
        db.session.commit()
        
        # Refresh component registry
        ComponentRegistry.refresh()
        
        return jsonify(component.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating component: {str(e)}")
        return jsonify({'error': str(e)}), 500


@role_bp.route('/components/<int:component_id>', methods=['PUT'])
@login_required
@require_permission('components', 'update')
def update_component(component_id):
    """Update a dashboard component"""
    try:
        component = DashboardComponent.query.get_or_404(component_id)
        data = request.get_json()
        
        if 'key' in data:
            existing = DashboardComponent.query.filter(
                DashboardComponent.key == data['key'],
                DashboardComponent.id != component_id
            ).first()
            if existing:
                return jsonify({'error': 'Component key already taken'}), 400
            component.key = data['key']
        
        if 'label' in data:
            component.label = data['label']
        if 'icon' in data:
            component.icon = data['icon']
        if 'component_name' in data:
            component.component_name = data['component_name']
        if 'path' in data:
            component.path = data['path']
        if 'description' in data:
            component.description = data['description']
        if 'section' in data:
            component.section = data['section']
        if 'is_active' in data:
            component.is_active = data['is_active']
        if 'order' in data:
            component.order = data['order']
        if 'required_permissions' in data:
            component.required_permissions = data['required_permissions']
        
        component.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Refresh component registry
        ComponentRegistry.refresh()
        
        return jsonify(component.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating component: {str(e)}")
        return jsonify({'error': str(e)}), 500


@role_bp.route('/components/<int:component_id>', methods=['DELETE'])
@login_required
@require_permission('components', 'delete')
def delete_component(component_id):
    """Delete a dashboard component"""
    try:
        component = DashboardComponent.query.get_or_404(component_id)
        
        # Check if component is assigned to any role
        assignment_count = RoleComponent.query.filter_by(component_id=component_id).count()
        if assignment_count > 0:
            return jsonify({
                'error': f'Cannot delete component assigned to {assignment_count} roles. Remove assignments first.'
            }), 400
        
        db.session.delete(component)
        db.session.commit()
        
        # Refresh component registry
        ComponentRegistry.refresh()
        
        return jsonify({'message': 'Component deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting component: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============ DASHBOARD CONFIG ============

@role_bp.route('/dashboard/config', methods=['GET'])
@login_required
def get_dashboard_config():
    """Get dashboard configuration for current user"""
    try:
        user = current_user
        
        from services.component_registry import ComponentRegistry
        config = ComponentRegistry.get_dashboard_config(user)
        
        return jsonify(config), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting dashboard config: {str(e)}")
        # Return empty config with user info
        return jsonify({
            'role': {
                'name': user.role if user else 'unknown',
                'id': user.role_id if user else None
            },
            'components': [],
            'user': {
                'id': user.id if user else None,
                'full_name': user.full_name if user else '',
                'email': user.email if user else ''
            }
        }), 200



# ============ USER ROLE ASSIGNMENT ============

@role_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@login_required
@require_permission('users', 'update')
def assign_user_role(user_id):
    """Assign a role to a user"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        role_id = data.get('role_id')
        
        if role_id:
            role = Role.query.get_or_404(role_id)
            user.role_id = role.id
            user.role = role.name
            user.is_active = True
            message = f'User assigned to {role.name}'
        else:
            # Remove role and suspend the user
            user.role_id = None
            user.role = None
            user.is_active = False
            message = 'User role removed and account suspended'
        
        db.session.commit()
        
        return jsonify({
            'message': message,
            'user': {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'role': user.role,
                'role_id': user.role_id,
                'is_active': user.is_active
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error assigning user role: {str(e)}")
        return jsonify({'error': str(e)}), 500


@role_bp.route('/roles/<int:role_id>/users', methods=['GET'])
@login_required
@require_permission('roles', 'read')
def get_role_users(role_id):
    """Get users assigned to a role"""
    try:
        role = Role.query.get_or_404(role_id)
        users = User.query.filter_by(role_id=role.id).all()
        return jsonify([{
            'id': u.id,
            'full_name': u.full_name,
            'email': u.email,
            'is_active': u.is_active,
            'created_at': u.created_at.isoformat() if u.created_at else None
        } for u in users]), 200
    except Exception as e:
        current_app.logger.error(f"Error getting role users: {str(e)}")
        return jsonify({'error': str(e)}), 500
    


@role_bp.route('/debug/permissions', methods=['GET'])
@login_required
def debug_permissions():
    """
    Get detailed permissions for current user.
    Used by frontend permissionService.
    """
    try:
        user = current_user
        permissions = get_user_permissions(user)
        
        return jsonify({
            'role': user.role,
            'role_id': user.role_id,
            'is_system': user.role in SYSTEM_ROLES,
            'permissions': permissions
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error in debug_permissions: {str(e)}")
        return jsonify({
            'role': user.role if user else 'unknown',
            'permissions': {}
        }), 200