from models import DashboardComponent, RoleComponent, Role, User
from flask_login import current_user

class ComponentService:
    
    # ✅ Define the exact components for super admin
    SUPER_ADMIN_COMPONENTS = [
        'overview',
        'products',
        'blog',
        'jobs',
        'outlets',
        'statistics',
        'contacts',
        'newsletter',
        'users',
        'permissions',
        'roles',
        'components',
        'tours',
        'tour-packages',
        'tour-calendar',
        'tour-payments',
        'tour-reports',
        'tour-staff',
        'partners',
        'partner-links',
        'partner-analytics',
        'profile',
        'activities'
    ]
    
    @staticmethod
    def get_user_components(user_id=None):
        """Get all components assigned to a user's roles"""
        user = User.query.get(user_id) if user_id else current_user
        
        if not user:
            return []
        
        # ✅ Super admin gets only the defined components
        if user.role == 'super_admin':
            return DashboardComponent.query.filter(
                DashboardComponent.key.in_(ComponentService.SUPER_ADMIN_COMPONENTS),
                DashboardComponent.is_active == True
            ).order_by(
                DashboardComponent.order
            ).all()
        
        # Get components from user's role(s)
        role_ids = []
        
        if user.role_id:
            role_ids.append(user.role_id)
        
        if user.role in ['admin', 'tour_manager', 'tour_assistant', 'partner']:
            role = Role.query.filter_by(name=user.role).first()
            if role:
                role_ids.append(role.id)
        
        if not role_ids:
            return []
        
        # Get all components from all user's roles
        components = DashboardComponent.query.join(
            RoleComponent, RoleComponent.component_id == DashboardComponent.id
        ).filter(
            RoleComponent.role_id.in_(role_ids),
            DashboardComponent.is_active == True
        ).order_by(
            DashboardComponent.order
        ).all()
        
        # Deduplicate
        seen = set()
        unique_components = []
        for comp in components:
            if comp.id not in seen:
                seen.add(comp.id)
                unique_components.append(comp)
        
        return unique_components
    
    @staticmethod
    def get_user_component_keys(user_id=None):
        """Get component keys assigned to a user"""
        components = ComponentService.get_user_components(user_id)
        return [comp.key for comp in components]
    
    @staticmethod
    def user_can_access_component(component_key, user_id=None):
        """Check if user can access a specific component"""
        user = User.query.get(user_id) if user_id else current_user
        
        if not user:
            return False
        
        # ✅ Super admin uses the allowed list
        if user.role == 'super_admin':
            return component_key in ComponentService.SUPER_ADMIN_COMPONENTS
        
        # Check if component exists
        component = DashboardComponent.query.filter_by(key=component_key).first()
        if not component:
            return False
        
        # Get user's role IDs
        role_ids = []
        if user.role_id:
            role_ids.append(user.role_id)
        
        role = Role.query.filter_by(name=user.role).first()
        if role:
            role_ids.append(role.id)
        
        if not role_ids:
            return False
        
        # Check if component is assigned to any of user's roles
        role_component = RoleComponent.query.filter(
            RoleComponent.role_id.in_(role_ids),
            RoleComponent.component_id == component.id
        ).first()
        
        return role_component is not None
    
    @staticmethod
    def get_components_by_section(user_id=None):
        """Get components grouped by section for sidebar"""
        components = ComponentService.get_user_components(user_id)
        
        sections = {}
        for comp in components:
            section = comp.section or 'Main'
            if section not in sections:
                sections[section] = []
            sections[section].append(comp)
        
        return sections