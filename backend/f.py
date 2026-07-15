"""
Role Component Management Script
Usage: python manage_role_components.py [command] [options]

Commands:
  list-roles                    - List all roles
  list-components               - List all components
  list-role-components <role>   - List components assigned to a role
  add-component <role> <component>  - Add component to role
  remove-component <role> <component> - Remove component from role
  show-role-users <role>        - Show users assigned to a role
  batch-remove <role>           - Interactive batch removal from a role
  find-component <component>    - Find which roles have a component
  stats                         - Show statistics
"""

import sys
import os
import re

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Role, DashboardComponent, RoleComponent, User

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_table(headers, rows):
    """Print a formatted table"""
    if not rows:
        print("  No data found")
        return
    
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, col in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(col)))
    
    # Print headers
    header_line = "│ " + " │ ".join(h.ljust(w) for h, w in zip(headers, col_widths)) + " │"
    separator = "├─" + "─┼─".join("─" * w for w in col_widths) + "─┤"
    top_line = "┌─" + "─┬─".join("─" * w for w in col_widths) + "─┐"
    bottom_line = "└─" + "─┴─".join("─" * w for w in col_widths) + "─┘"
    
    print(top_line)
    print(header_line)
    print(separator)
    
    for row in rows:
        row_line = "│ " + " │ ".join(str(col).ljust(w) for col, w in zip(row, col_widths)) + " │"
        print(row_line)
    
    print(bottom_line)

def list_roles():
    """List all roles in the system"""
    with app.app_context():
        roles = Role.query.order_by(Role.name).all()
        
        print_header("📋 ALL ROLES")
        
        headers = ["ID", "Name", "Description", "System", "Active", "Users", "Components"]
        rows = []
        for role in roles:
            user_count = len(role.users) if hasattr(role, 'users') else 0
            comp_count = len(role.components) if hasattr(role, 'components') else 0
            rows.append([
                role.id,
                role.name,
                role.description[:30] + "..." if role.description and len(role.description) > 30 else (role.description or ""),
                "✅" if role.is_system else "❌",
                "✅" if role.is_active else "❌",
                user_count,
                comp_count
            ])
        
        print_table(headers, rows)
        print(f"\nTotal: {len(roles)} roles")

def list_components():
    """List all components in the system"""
    with app.app_context():
        components = DashboardComponent.query.order_by(DashboardComponent.section, DashboardComponent.order).all()
        
        print_header("📦 ALL COMPONENTS")
        
        headers = ["ID", "Key", "Label", "Section", "Active"]
        rows = []
        for comp in components:
            rows.append([
                comp.id,
                comp.key,
                comp.label,
                comp.section or "Uncategorized",
                "✅" if comp.is_active else "❌"
            ])
        
        print_table(headers, rows)
        print(f"\nTotal: {len(components)} components")

def list_role_components(role_identifier):
    """List components assigned to a specific role"""
    with app.app_context():
        # Find role by name or ID
        role = None
        if role_identifier.isdigit():
            role = Role.query.get(int(role_identifier))
        else:
            role = Role.query.filter_by(name=role_identifier).first()
        
        if not role:
            print(f"❌ Role '{role_identifier}' not found")
            return
        
        print_header(f"📋 COMPONENTS FOR ROLE: {role.name} (ID: {role.id})")
        
        # Get components
        role_components = RoleComponent.query.filter_by(role_id=role.id).join(
            DashboardComponent
        ).order_by(DashboardComponent.section, DashboardComponent.order).all()
        
        headers = ["ID", "Key", "Label", "Section"]
        rows = []
        for rc in role_components:
            comp = DashboardComponent.query.get(rc.component_id)
            if comp:
                rows.append([
                    comp.id,
                    comp.key,
                    comp.label,
                    comp.section or "Uncategorized"
                ])
        
        if rows:
            print_table(headers, rows)
            print(f"\nTotal: {len(rows)} components assigned to '{role.name}'")
        else:
            print(f"\n⚠️ No components assigned to '{role.name}'")

def find_component(component_key):
    """Find which roles have a specific component"""
    with app.app_context():
        component = DashboardComponent.query.filter_by(key=component_key).first()
        if not component:
            print(f"❌ Component '{component_key}' not found")
            return
        
        print_header(f"🔍 ROLES WITH COMPONENT: {component.label} ({component.key})")
        
        # Find roles with this component
        role_components = RoleComponent.query.filter_by(component_id=component.id).join(Role).all()
        
        headers = ["Role ID", "Role Name", "System", "Active", "Users"]
        rows = []
        for rc in role_components:
            role = Role.query.get(rc.role_id)
            if role:
                user_count = len(role.users) if hasattr(role, 'users') else 0
                rows.append([
                    role.id,
                    role.name,
                    "✅" if role.is_system else "❌",
                    "✅" if role.is_active else "❌",
                    user_count
                ])
        
        if rows:
            print_table(headers, rows)
            print(f"\nTotal: {len(rows)} roles have '{component_key}'")
        else:
            print(f"\n⚠️ No roles have '{component_key}'")

def add_component(role_identifier, component_key):
    """Add a component to a role"""
    with app.app_context():
        # Find role
        role = None
        if role_identifier.isdigit():
            role = Role.query.get(int(role_identifier))
        else:
            role = Role.query.filter_by(name=role_identifier).first()
        
        if not role:
            print(f"❌ Role '{role_identifier}' not found")
            return
        
        # Find component
        component = DashboardComponent.query.filter_by(key=component_key).first()
        if not component:
            print(f"❌ Component '{component_key}' not found")
            return
        
        # Check if already assigned
        existing = RoleComponent.query.filter_by(
            role_id=role.id,
            component_id=component.id
        ).first()
        
        if existing:
            print(f"⚠️ Component '{component_key}' is already assigned to role '{role.name}'")
            return
        
        # Add component
        new_rc = RoleComponent(
            role_id=role.id,
            component_id=component.id
        )
        db.session.add(new_rc)
        db.session.commit()
        
        print(f"✅ Added component '{component_key}' to role '{role.name}'")

def remove_component(role_identifier, component_key):
    """Remove a component from a role"""
    with app.app_context():
        # Find role
        role = None
        if role_identifier.isdigit():
            role = Role.query.get(int(role_identifier))
        else:
            role = Role.query.filter_by(name=role_identifier).first()
        
        if not role:
            print(f"❌ Role '{role_identifier}' not found")
            return
        
        # Find component
        component = DashboardComponent.query.filter_by(key=component_key).first()
        if not component:
            print(f"❌ Component '{component_key}' not found")
            return
        
        # Check if assigned
        existing = RoleComponent.query.filter_by(
            role_id=role.id,
            component_id=component.id
        ).first()
        
        if not existing:
            print(f"⚠️ Component '{component_key}' is not assigned to role '{role.name}'")
            return
        
        # Remove component
        db.session.delete(existing)
        db.session.commit()
        
        print(f"✅ Removed component '{component_key}' from role '{role.name}'")

def batch_remove(role_identifier):
    """Interactive batch removal of components from a role"""
    with app.app_context():
        # Find role
        role = None
        if role_identifier.isdigit():
            role = Role.query.get(int(role_identifier))
        else:
            role = Role.query.filter_by(name=role_identifier).first()
        
        if not role:
            print(f"❌ Role '{role_identifier}' not found")
            return
        
        # Get components
        role_components = RoleComponent.query.filter_by(role_id=role.id).join(
            DashboardComponent
        ).order_by(DashboardComponent.section, DashboardComponent.order).all()
        
        if not role_components:
            print(f"⚠️ No components assigned to '{role.name}'")
            return
        
        print_header(f"🗑️ BATCH REMOVE: Components from '{role.name}'")
        
        # Display components with numbers
        comps = []
        for i, rc in enumerate(role_components, 1):
            comp = DashboardComponent.query.get(rc.component_id)
            if comp:
                comps.append(comp)
                print(f"  {i}. {comp.key} - {comp.label} ({comp.section})")
        
        print("\nOptions:")
        print("  Enter numbers separated by commas (e.g., 1,3,5)")
        print("  Enter 'all' to remove all components")
        print("  Enter 'q' to quit")
        
        choice = input("\nSelect components to remove: ").strip()
        
        if choice.lower() == 'q':
            print("Cancelled")
            return
        
        if choice.lower() == 'all':
            confirm = input(f"⚠️ Remove ALL {len(comps)} components from '{role.name}'? (yes/no): ")
            if confirm.lower() == 'yes':
                for comp in comps:
                    rc = RoleComponent.query.filter_by(
                        role_id=role.id,
                        component_id=comp.id
                    ).first()
                    if rc:
                        db.session.delete(rc)
                db.session.commit()
                print(f"✅ Removed ALL {len(comps)} components from '{role.name}'")
            else:
                print("Cancelled")
            return
        
        # Parse selection
        selected = []
        for part in choice.split(','):
            part = part.strip()
            if part.isdigit():
                idx = int(part) - 1
                if 0 <= idx < len(comps):
                    selected.append(comps[idx])
                else:
                    print(f"⚠️ Invalid number: {part}")
        
        if not selected:
            print("No valid selections made")
            return
        
        # Confirm and remove
        print(f"\nComponents to remove: {len(selected)}")
        for comp in selected:
            print(f"  - {comp.key} - {comp.label}")
        
        confirm = input(f"\nRemove these components from '{role.name}'? (yes/no): ")
        if confirm.lower() == 'yes':
            for comp in selected:
                rc = RoleComponent.query.filter_by(
                    role_id=role.id,
                    component_id=comp.id
                ).first()
                if rc:
                    db.session.delete(rc)
            db.session.commit()
            print(f"✅ Removed {len(selected)} components from '{role.name}'")
        else:
            print("Cancelled")

def show_role_users(role_identifier):
    """Show users assigned to a role"""
    with app.app_context():
        # Find role
        role = None
        if role_identifier.isdigit():
            role = Role.query.get(int(role_identifier))
        else:
            role = Role.query.filter_by(name=role_identifier).first()
        
        if not role:
            print(f"❌ Role '{role_identifier}' not found")
            return
        
        print_header(f"👥 USERS ASSIGNED TO: {role.name}")
        
        users = User.query.filter_by(role_id=role.id).all()
        if not users:
            # Check system role names
            users = User.query.filter_by(role=role.name).all()
        
        headers = ["ID", "Email", "Full Name", "Active", "Created At"]
        rows = []
        for user in users:
            rows.append([
                user.id,
                user.email,
                user.full_name,
                "✅" if user.is_active else "❌",
                user.created_at.strftime("%Y-%m-%d %H:%M") if user.created_at else "N/A"
            ])
        
        if rows:
            print_table(headers, rows)
            print(f"\nTotal: {len(rows)} users assigned to '{role.name}'")
        else:
            print(f"\n⚠️ No users assigned to '{role.name}'")

def show_stats():
    """Show system statistics"""
    with app.app_context():
        print_header("📊 SYSTEM STATISTICS")
        
        total_roles = Role.query.count()
        total_components = DashboardComponent.query.count()
        total_assignments = RoleComponent.query.count()
        total_users = User.query.count()
        
        print(f"  Total Roles:        {total_roles}")
        print(f"  Total Components:   {total_components}")
        print(f"  Total Assignments:  {total_assignments}")
        print(f"  Total Users:        {total_users}")
        
        print("\n📋 ROLES WITH COMPONENT COUNT:")
        roles = Role.query.all()
        for role in roles:
            count = RoleComponent.query.filter_by(role_id=role.id).count()
            print(f"  - {role.name}: {count} components")
        
        print("\n📋 COMPONENTS BY SECTION:")
        sections = {}
        components = DashboardComponent.query.all()
        for comp in components:
            section = comp.section or "Uncategorized"
            sections[section] = sections.get(section, 0) + 1
        
        for section, count in sorted(sections.items()):
            print(f"  - {section}: {count} components")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    
    if command == "list-roles":
        list_roles()
    elif command == "list-components":
        list_components()
    elif command == "list-role-components" and len(sys.argv) > 2:
        list_role_components(sys.argv[2])
    elif command == "find-component" and len(sys.argv) > 2:
        find_component(sys.argv[2])
    elif command == "add-component" and len(sys.argv) > 3:
        add_component(sys.argv[2], sys.argv[3])
    elif command == "remove-component" and len(sys.argv) > 3:
        remove_component(sys.argv[2], sys.argv[3])
    elif command == "batch-remove" and len(sys.argv) > 2:
        batch_remove(sys.argv[2])
    elif command == "show-role-users" and len(sys.argv) > 2:
        show_role_users(sys.argv[2])
    elif command == "stats":
        show_stats()
    else:
        print(f"❌ Unknown command: {command}")
        print(__doc__)

if __name__ == "__main__":
    main()