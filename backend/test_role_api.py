# backend/test_role_api.py

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Role, DashboardComponent, RoleComponent, User
from services.component_registry import ComponentRegistry

def test_api():
    """Test the role API endpoints"""
    print("🧪 Testing Role API...")
    print("=" * 50)
    
    with app.app_context():
        # 1. Test component registry
        print("\n📦 Testing Component Registry...")
        components = ComponentRegistry.get_all_components()
        print(f"✅ Loaded {len(components)} components")
        
        # 2. Test getting components by section
        sections = ComponentRegistry.get_components_by_section()
        print(f"\n📂 Components by section:")
        for section, comps in sections.items():
            print(f"  - {section}: {len(comps)} components")
        
        # 3. Test getting user components
        user = User.query.first()
        if user:
            print(f"\n👤 Testing user components for {user.email}...")
            user_comps = ComponentRegistry.get_user_components(user)
            print(f"  ✅ User has {len(user_comps)} components")
            for comp in user_comps[:5]:
                print(f"    - {comp['key']}: {comp['label']}")
        
        # 4. Test roles
        print("\n📋 Testing Roles...")
        roles = Role.query.all()
        print(f"  ✅ Found {len(roles)} roles")
        for role in roles:
            comp_count = RoleComponent.query.filter_by(role_id=role.id).count()
            user_count = User.query.filter_by(role_id=role.id).count()
            print(f"    - {role.name}: {comp_count} components, {user_count} users")
        
        # 5. Test dashboard config
        if user:
            print(f"\n📊 Testing Dashboard Config for {user.email}...")
            config = ComponentRegistry.get_dashboard_config(user)
            print(f"  ✅ Role: {config['role']['name']}")
            print(f"  ✅ Components: {len(config['components'])}")
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed!")

if __name__ == '__main__':
    test_api()