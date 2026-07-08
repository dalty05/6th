# backend/assign_partner_components.py

from app import app, db
from models import Role, DashboardComponent, RoleComponent  # ✅ Add Role import

def assign_partner_components():
    """Assign partner components to the partner role"""
    
    with app.app_context():
        print("=" * 60)
        print("🔗 Assigning Partner Components to Partner Role")
        print("=" * 60)
        
        # Find the partner role
        partner_role = Role.query.filter_by(name='partner').first()
        
        if not partner_role:
            print("❌ Partner role not found! Creating it...")
            partner_role = Role(
                name='partner',
                description='Marketing Partner Role',
                is_system=True,
                is_active=True
            )
            db.session.add(partner_role)
            db.session.commit()
            print(f"✅ Created partner role (ID: {partner_role.id})")
        
        print(f"📝 Partner Role: {partner_role.name} (ID: {partner_role.id})")
        
        # Partner component keys to assign
        partner_component_keys = [
            'partner-dashboard',
            'partner-links',
            'partner-analytics',
            'partner-profile',
            'partner-help'
        ]
        
        assigned_count = 0
        already_assigned_count = 0
        
        for key in partner_component_keys:
            # Find the component
            component = DashboardComponent.query.filter_by(key=key).first()
            
            if not component:
                print(f"❌ Component not found: {key}")
                continue
            
            # Check if already assigned
            existing = RoleComponent.query.filter_by(
                role_id=partner_role.id,
                component_id=component.id
            ).first()
            
            if existing:
                print(f"ℹ️ Already assigned: {key}")
                already_assigned_count += 1
            else:
                # Assign component to role
                role_component = RoleComponent(
                    role_id=partner_role.id,
                    component_id=component.id
                )
                db.session.add(role_component)
                assigned_count += 1
                print(f"✅ Assigned: {key} → {partner_role.name}")
        
        db.session.commit()
        
        print("\n" + "=" * 60)
        print(f"📊 Summary:")
        print(f"  ✅ New assignments: {assigned_count}")
        print(f"  🔄 Already assigned: {already_assigned_count}")
        print("=" * 60)
        
        # Show all components assigned to partner role
        print("\n📋 Components assigned to Partner Role:")
        role_components = RoleComponent.query.filter_by(role_id=partner_role.id).all()
        for rc in role_components:
            comp = DashboardComponent.query.get(rc.component_id)
            if comp:
                print(f"  - {comp.key} ({comp.section}) - {comp.label}")

if __name__ == '__main__':
    assign_partner_components()