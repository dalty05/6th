# backend/seed_role_components.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Role, DashboardComponent, RoleComponent

with app.app_context():
    print("🔍 Seeding role-component assignments...")
    
    try:
        # Get all roles and components
        roles = Role.query.all()
        components = DashboardComponent.query.all()
        
        print(f"📋 Found {len(roles)} roles and {len(components)} components")
        
        # Clear existing assignments
        RoleComponent.query.delete()
        db.session.commit()
        print("✅ Cleared existing assignments")
        
        # Define assignments
        role_assignments = {
            'super_admin': [c.key for c in components],  # All components
            'admin': ['overview', 'products', 'blog', 'jobs', 'outlets', 'statistics', 'contacts', 'newsletter',
                      'tours', 'tour-packages', 'tour-calendar', 'tour-staff'],
            'tour_manager': ['overview', 'tours', 'tour-packages', 'tour-calendar', 'tour-staff', 'statistics'],
            'tour_assistant': ['overview', 'tours', 'statistics'],
            'partner': ['overview']
        }
        
        assignment_count = 0
        for role_name, component_keys in role_assignments.items():
            role = Role.query.filter_by(name=role_name).first()
            if role:
                for idx, key in enumerate(component_keys):
                    comp = DashboardComponent.query.filter_by(key=key).first()
                    if comp:
                        # Check if already exists
                        existing = RoleComponent.query.filter_by(
                            role_id=role.id,
                            component_id=comp.id
                        ).first()
                        if not existing:
                            rc = RoleComponent(
                                role_id=role.id,
                                component_id=comp.id,
                                order=idx
                            )
                            db.session.add(rc)
                            assignment_count += 1
                print(f"  ✅ Assigned components to {role_name}")
        
        db.session.commit()
        print(f"✅ Created {assignment_count} role-component assignments")
        
        # Verify
        print("\n📋 Verification:")
        for role in roles:
            count = RoleComponent.query.filter_by(role_id=role.id).count()
            print(f"  - {role.name}: {count} components")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")
    
    print("🎉 Done!")