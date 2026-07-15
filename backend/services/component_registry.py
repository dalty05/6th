from models import DashboardComponent, RoleComponent, Role, User
from flask import current_app
import json
import sys

class ComponentRegistry:
    """
    Central registry for all dashboard components.
    Caches component data to reduce database queries.
    """
    
    _components = None
    _component_map = None
    _role_component_map = None
    _loaded = False
    
    @classmethod
    def load_components(cls, force=False):
        """Load all components from database"""
        if cls._loaded and not force:
            return cls._components
        
        try:
            # Use raw SQL to avoid recursion issues
            from sqlalchemy import text
            from app import db
            
            # Get all columns from the table
            result = db.session.execute(text("PRAGMA table_info(dashboard_components)"))
            existing_cols = [row[1] for row in result]
            
            # Build select query with available columns
            select_cols = ['id', 'key', 'label', 'icon', 'component_name', 'path', 
                          'description', 'section', 'is_active', '"order"']
            
            # Add optional columns if they exist
            for col in ['required_permissions', 'created_at', 'updated_at']:
                if col in existing_cols:
                    select_cols.append(col)
            
            select_str = ', '.join(select_cols)
            
            query = text(f"""
                SELECT {select_str}
                FROM dashboard_components 
                WHERE is_active = 1 
                ORDER BY section, "order"
            """)
            
            result = db.session.execute(query)
            
            cls._components = []
            cls._component_map = {}
            
            for row in result:
                comp_dict = {}
                for idx, col in enumerate(select_cols):
                    col_name = col.strip('"')
                    value = row[idx]
                    if col_name == 'required_permissions' and value:
                        try:
                            value = json.loads(value) if isinstance(value, str) else value
                        except:
                            value = []
                    comp_dict[col_name] = value
                
                comp_dict.setdefault('required_permissions', [])
                comp_dict.setdefault('created_at', None)
                comp_dict.setdefault('updated_at', None)
                
                if 'key' not in comp_dict:
                    continue
                    
                cls._components.append(comp_dict)
                cls._component_map[comp_dict['key']] = comp_dict
            
            # Build role-component mapping
            cls._build_role_component_map()
            
            cls._loaded = True
            current_app.logger.info(f"✅ Component registry loaded: {len(cls._components)} components")
            
        except Exception as e:
            current_app.logger.error(f"❌ Failed to load component registry: {str(e)}")
            import traceback
            traceback.print_exc()
            cls._components = []
            cls._component_map = {}
            cls._loaded = False
        
        return cls._components
    
    @classmethod
    def _build_role_component_map(cls):
        """Build a cache of role -> components mapping using raw SQL"""
        try:
            from sqlalchemy import text
            from app import db
            
            cls._role_component_map = {}
            
            # ✅ Use raw SQL to avoid ORM relationship issues
            query = text("""
                SELECT rc.role_id, rc.component_id, rc."order", dc.key
                FROM role_components rc
                JOIN dashboard_components dc ON dc.id = rc.component_id
                ORDER BY rc.role_id, rc."order"
            """)
            
            result = db.session.execute(query)
            
            for row in result:
                role_id = row[0]
                if role_id not in cls._role_component_map:
                    cls._role_component_map[role_id] = []
                cls._role_component_map[role_id].append({
                    'component_id': row[1],
                    'order': row[2],
                    'component_key': row[3]
                })
                
            current_app.logger.debug(f"✅ Built role-component cache for {len(cls._role_component_map)} roles")
            
        except Exception as e:
            current_app.logger.error(f"❌ Failed to build role-component map: {str(e)}")
            import traceback
            traceback.print_exc()
            cls._role_component_map = {}
    
    @classmethod
    def get_component(cls, key):
        """Get a single component by key"""
        if not cls._loaded:
            cls.load_components()
        return cls._component_map.get(key) if cls._component_map else None
    
    @classmethod
    def get_all_components(cls):
        """Get all components"""
        if not cls._loaded:
            cls.load_components()
        return cls._components or []
    
    @classmethod
    def get_components_by_section(cls):
        """Get components grouped by section"""
        if not cls._loaded:
            cls.load_components()
        
        sections = {}
        for comp in cls._components or []:
            section = comp.get('section', 'Main')
            if section not in sections:
                sections[section] = []
            sections[section].append(comp)
        
        return sections
    
    @classmethod
    def get_components_for_role(cls, role_id):
        """Get all components assigned to a specific role"""
        if not cls._loaded:
            cls.load_components()
        
        if not cls._role_component_map:
            return []
        
        if role_id not in cls._role_component_map:
            return []
        
        components = []
        for rc in cls._role_component_map[role_id]:
            comp = cls._component_map.get(rc['component_key']) if cls._component_map else None
            if comp:
                comp_copy = comp.copy()
                comp_copy['order'] = rc['order']
                components.append(comp_copy)
        
        return sorted(components, key=lambda x: x.get('order', 0))
    
    @classmethod
    def get_user_components(cls, user):
        """Get all components for a specific user based on their role"""
        if not user:
            return []
        
        role_id = user.role_id if hasattr(user, 'role_id') else None
        
        if not role_id and user.role:
            try:
                from models import Role
                role = Role.query.filter(Role.name.ilike(user.role)).first()
                if role:
                    role_id = role.id
            except:
                pass
        
        if not role_id:
            default = cls.get_component('overview')
            return [default] if default else []
        
        return cls.get_components_for_role(role_id)
    
    @classmethod
    def has_component(cls, user, component_key):
        """Check if a user has access to a specific component"""
        if not user:
            return False
        
        if user.role == 'super_admin':
            return True
        
        components = cls.get_user_components(user)
        return any(c.get('key') == component_key for c in components)
    
    @classmethod
    def refresh(cls):
        """Refresh the component cache"""
        cls._loaded = False
        cls._components = None
        cls._component_map = None
        cls._role_component_map = None
        cls.load_components()
        current_app.logger.info("🔄 Component registry refreshed")
    
    @classmethod
    def get_dashboard_config(cls, user):
        """Get complete dashboard configuration for a user"""
        components = cls.get_user_components(user)
        
        role_name = user.role
        if user.role_id:
            try:
                from models import Role
                role = Role.query.get(user.role_id)
                if role:
                    role_name = role.name
            except:
                pass
        
        return {
            'role': {
                'name': role_name,
                'id': user.role_id
            },
            'components': components,
            'user': {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email
            }
        }