"""
Role and Component Management Script
Usage: python manage_components.py [command] [options]

Commands:
  list-roles                    - List all roles
  list-components               - List all components
  list-role-components <role>   - List components assigned to a role
  add-component <role> <component>  - Add component to role
  remove-component <role> <component> - Remove component from role
  delete-component <component>  - Delete a component and its assignments
  batch-delete-components       - Interactive batch deletion of components
  show-role-users <role>        - Show users assigned to a role
  find-component <component>    - Find which roles have a component
  stats                         - Show statistics
  cleanup-orphaned              - Remove orphaned component assignments
"""

import sys
import os
import re
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Role, DashboardComponent, RoleComponent, User

def print_header(title, char="="):
    """Print a formatted header"""
    print("\n" + char * 70)
    print(f"  {title}")
    print(char * 70)

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
            comp_count = RoleComponent.query.filter_by(role_id=role.id).count()
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
        
        headers = ["ID", "Key", "Label", "Section", "Active", "Roles"]
        rows = []
        for comp in components:
            role_count = RoleComponent.query.filter_by(component_id=comp.id).count()
            rows.append([
                comp.id,
                comp.key,
                comp.label,
                comp.section or "Uncategorized",
                "✅" if comp.is_active else "❌",
                role_count
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

def delete_component(component_key, force=False):
    """Delete a component and all its assignments from the system"""
    with app.app_context():
        # Find component
        component = DashboardComponent.query.filter_by(key=component_key).first()
        if not component:
            print(f"❌ Component '{component_key}' not found")
            return
        
        print_header(f"🗑️ DELETE COMPONENT: {component.label} ({component.key})")
        print(f"  ID: {component.id}")
        print(f"  Section: {component.section or 'Uncategorized'}")
        print(f"  Active: {component.is_active}")
        
        # Check assignments
        assignments = RoleComponent.query.filter_by(component_id=component.id).all()
        roles_with_component = []
        for rc in assignments:
            role = Role.query.get(rc.role_id)
            if role:
                roles_with_component.append(role.name)
        
        if assignments:
            print(f"\n⚠️ This component is assigned to {len(assignments)} role(s):")
            for role_name in roles_with_component:
                print(f"  - {role_name}")
        else:
            print("\n✅ No roles have this component assigned")
        
        if not force:
            print("\nOptions:")
            print("  yes - Confirm deletion")
            print("  no - Cancel")
            choice = input("\nAre you sure you want to delete this component? (yes/no): ").strip().lower()
            
            if choice != 'yes':
                print("❌ Deletion cancelled")
                return
        
        # Delete all assignments first
        for rc in assignments:
            db.session.delete(rc)
            print(f"  ✅ Removed assignment from role: {Role.query.get(rc.role_id).name}")
        
        # Delete the component
        db.session.delete(component)
        db.session.commit()
        
        print(f"\n✅ Component '{component_key}' has been permanently deleted")
        print(f"   Removed {len(assignments)} role assignments")

def batch_delete_components():
    """Interactive batch deletion of components"""
    with app.app_context():
        components = DashboardComponent.query.order_by(
            DashboardComponent.section, DashboardComponent.order
        ).all()
        
        if not components:
            print("⚠️ No components found in the system")
            return
        
        print_header("🗑️ BATCH DELETE COMPONENTS")
        
        # Display components with numbers
        comp_list = []
        for i, comp in enumerate(components, 1):
            role_count = RoleComponent.query.filter_by(component_id=comp.id).count()
            comp_list.append(comp)
            print(f"  {i}. {comp.key} - {comp.label} ({comp.section or 'Uncategorized'}) - {role_count} role(s)")
        
        print("\nOptions:")
        print("  Enter numbers separated by commas (e.g., 1,3,5)")
        print("  Enter 'all' to delete all components")
        print("  Enter 'q' to quit")
        
        choice = input("\nSelect components to delete: ").strip()
        
        if choice.lower() == 'q':
            print("Cancelled")
            return
        
        if choice.lower() == 'all':
            print(f"\n⚠️ You are about to delete ALL {len(comp_list)} components")
            print("This will also remove all role assignments for these components")
            confirm = input("Are you sure? (yes/no): ")
            if confirm.lower() == 'yes':
                for comp in comp_list:
                    # Delete assignments
                    assignments = RoleComponent.query.filter_by(component_id=comp.id).all()
                    for rc in assignments:
                        db.session.delete(rc)
                    db.session.delete(comp)
                db.session.commit()
                print(f"✅ Deleted ALL {len(comp_list)} components")
            else:
                print("Cancelled")
            return
        
        # Parse selection
        selected = []
        for part in choice.split(','):
            part = part.strip()
            if part.isdigit():
                idx = int(part) - 1
                if 0 <= idx < len(comp_list):
                    selected.append(comp_list[idx])
                else:
                    print(f"⚠️ Invalid number: {part}")
        
        if not selected:
            print("No valid selections made")
            return
        
        # Show summary
        print(f"\nComponents to delete: {len(selected)}")
        for comp in selected:
            role_count = RoleComponent.query.filter_by(component_id=comp.id).count()
            print(f"  - {comp.key} - {comp.label} ({role_count} role(s))")
        
        confirm = input(f"\nDelete these {len(selected)} components? (yes/no): ")
        if confirm.lower() == 'yes':
            for comp in selected:
                # Delete assignments
                assignments = RoleComponent.query.filter_by(component_id=comp.id).all()
                for rc in assignments:
                    db.session.delete(rc)
                db.session.delete(comp)
            db.session.commit()
            print(f"✅ Deleted {len(selected)} components")
        else:
            print("Cancelled")

def cleanup_orphaned():
    """Remove orphaned component assignments (components that don't exist)"""
    with app.app_context():
        print_header("🧹 CLEANUP ORPHANED ASSIGNMENTS")
        
        # Find all role components
        all_rc = RoleComponent.query.all()
        orphaned = []
        
        for rc in all_rc:
            comp = DashboardComponent.query.get(rc.component_id)
            if not comp:
                orphaned.append(rc)
        
        if not orphaned:
            print("✅ No orphaned assignments found")
            return
        
        print(f"Found {len(orphaned)} orphaned assignment(s)")
        for rc in orphaned:
            role = Role.query.get(rc.role_id)
            print(f"  - Role: {role.name if role else 'Unknown'} (Role ID: {rc.role_id}), Component ID: {rc.component_id}")
        
        confirm = input(f"\nDelete these {len(orphaned)} orphaned assignments? (yes/no): ")
        if confirm.lower() == 'yes':
            for rc in orphaned:
                db.session.delete(rc)
            db.session.commit()
            print(f"✅ Deleted {len(orphaned)} orphaned assignments")
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
        
        # Check for orphaned assignments
        orphaned = 0
        all_rc = RoleComponent.query.all()
        for rc in all_rc:
            comp = DashboardComponent.query.get(rc.component_id)
            if not comp:
                orphaned += 1
        
        print(f"  Total Roles:        {total_roles}")
        print(f"  Total Components:   {total_components}")
        print(f"  Total Assignments:  {total_assignments}")
        print(f"  Total Users:        {total_users}")
        print(f"  Orphaned Assignments: {orphaned}")
        
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
        
        if orphaned > 0:
            print(f"\n⚠️ {orphaned} orphaned assignments detected. Run 'cleanup-orphaned' to fix.")

def interactive_mode():
    """Interactive mode for component management"""
    print_header("🛠️ COMPONENT MANAGEMENT INTERACTIVE MODE")
    
    commands = {
        '1': ('List all roles', list_roles),
        '2': ('List all components', list_components),
        '3': ('List components for a role', lambda: list_role_components(input("Enter role name or ID: "))),
        '4': ('Add component to role', lambda: add_component(input("Enter role name or ID: "), input("Enter component key: "))),
        '5': ('Remove component from role', lambda: remove_component(input("Enter role name or ID: "), input("Enter component key: "))),
        '6': ('Delete a component', lambda: delete_component(input("Enter component key: "))),
        '7': ('Batch delete components', batch_delete_components),
        '8': ('Find component in roles', lambda: find_component(input("Enter component key: "))),
        '9': ('Cleanup orphaned assignments', cleanup_orphaned),
        '10': ('Show statistics', show_stats),
        'q': ('Quit', None)
    }
    
    while True:
        print("\n" + "-" * 40)
        print("Available commands:")
        for key, (desc, _) in commands.items():
            print(f"  {key}. {desc}")
        
        choice = input("\nSelect an option: ").strip().lower()
        
        if choice == 'q':
            print("Goodbye!")
            break
        
        if choice in commands:
            cmd_name, cmd_func = commands[choice]
            if cmd_func:
                try:
                    cmd_func()
                except Exception as e:
                    print(f"❌ Error: {e}")
            else:
                print("Goodbye!")
                break
        else:
            print("❌ Invalid option. Please try again.")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nFor interactive mode, run: python manage_components.py --interactive")
        return
    
    command = sys.argv[1].lower()
    
    # Interactive mode
    if command == "--interactive" or command == "-i":
        interactive_mode()
        return
    
    # Command mode
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
    elif command == "delete-component" and len(sys.argv) > 2:
        force = "--force" in sys.argv
        delete_component(sys.argv[2], force)
    elif command == "batch-delete-components":
        batch_delete_components()
    elif command == "cleanup-orphaned":
        cleanup_orphaned()
    elif command == "show-role-users" and len(sys.argv) > 2:
        show_role_users(sys.argv[2])
    elif command == "stats":
        show_stats()
    else:
        print(f"❌ Unknown command: {command}")
        print(__doc__)

if __name__ == "__main__":
    main()