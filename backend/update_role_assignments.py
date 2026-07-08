# backend/update_role_assignments.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Role, DashboardComponent, RoleComponent

with app.app_context():
    print("🔍 Updating role assignments...")
    
    # Define full role assignments
    role_assignments = {
        'super_admin': [
            'overview', 'products', 'blog', 'jobs', 'outlets', 'statistics', 
            'contacts', 'newsletter', 'users', 'permissions', 'roles', 
            'tours', 'tour-packages', 'tour-calendar', 'tour-payments', 
            'tour-reports', 'tour-staff', 'partner-dashboard'
        ],
        'admin': [
            'overview', 'products', 'blog', 'jobs', 'outlets', 'statistics', 
            'contacts', 'newsletter', 'tours', 'tour-packages', 
            'tour-calendar', 'tour-payments', 'tour-reports', 'tour-staff'
        ],
        'tour_manager': [
            'overview', 'tours', 'tour-packages', 'tour-calendar', 
            'tour-payments', 'tour-reports', 'tour-staff', 'statistics'
        ],
        'tour_assistant': [
            'overview', 'tours', 'tour-calendar', 'statistics'
        ],
        'partner': [
            'overview', 'partner-dashboard', 'partner-links', 'partner-analytics'
        ]
    }
    
    updated_count = 0
    for role_name, component_keys in role_assignments.items():
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            print(f"⚠️ Role {role_name} not found, skipping...")
            continue
        
        print(f"📋 Updating {role_name}...")
        
        # Clear existing assignments
        RoleComponent.query.filter_by(role_id=role.id).delete()
        
        # Add new assignments
        for idx, key in enumerate(component_keys):
            comp = DashboardComponent.query.filter_by(key=key).first()
            if comp:
                rc = RoleComponent(
                    role_id=role.id,
                    component_id=comp.id,
                    order=idx
                )
                db.session.add(rc)
                updated_count += 1
        
        print(f"  ✅ Assigned {len(component_keys)} components to {role_name}")
    
    db.session.commit()
    print(f"\n✅ Updated {updated_count} role-component assignments")