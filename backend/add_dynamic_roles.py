# backend/migrations/add_dynamic_roles.py

from flask import current_app
from app import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def upgrade():
    """Add dynamic role tables and seed initial data"""
    try:
        logger.info("🚀 Starting dynamic roles migration...")
        
        # Import models here to avoid circular imports
        from models import Role, DashboardComponent, RoleComponent, User
        
        # Create tables (if using SQLAlchemy's create_all)
        db.create_all()
        
        # Check if tables already have data
        if Role.query.first():
            logger.info("⚠️ Roles already exist, skipping seed...")
            return
        
        # ============ SEED DEFAULT ROLES ============
        logger.info("📦 Seeding default roles...")
        
        default_roles = [
            {
                'name': 'super_admin',
                'description': 'Full system access with all permissions',
                'is_system': True,
                'is_active': True
            },
            {
                'name': 'admin',
                'description': 'Administrative access with limited user management',
                'is_system': True,
                'is_active': True
            },
            {
                'name': 'tour_manager',
                'description': 'Manage factory tours and bookings',
                'is_system': True,
                'is_active': True
            },
            {
                'name': 'tour_assistant',
                'description': 'Assist with tour operations',
                'is_system': True,
                'is_active': True
            },
            {
                'name': 'partner',
                'description': 'Marketing partner with referral access',
                'is_system': True,
                'is_active': True
            }
        ]
        
        roles = {}
        for role_data in default_roles:
            role = Role(**role_data)
            db.session.add(role)
            db.session.flush()  # Get the ID
            roles[role_data['name']] = role
            logger.info(f"  ✅ Created role: {role_data['name']}")
        
        db.session.commit()
        
        # ============ SEED DEFAULT COMPONENTS ============
        logger.info("📦 Seeding default dashboard components...")
        
        default_components = [
            {
                'key': 'overview',
                'label': 'Dashboard',
                'icon': 'fas fa-tachometer-alt',
                'component_name': 'Overview',
                'path': '/admin/dashboard',
                'description': 'Main dashboard overview',
                'section': 'Main',
                'order': 1
            },
            {
                'key': 'products',
                'label': 'Products',
                'icon': 'fas fa-box-open',
                'component_name': 'ProductsManagement',
                'path': '/admin/products',
                'description': 'Manage dairy products',
                'section': 'Main',
                'order': 2,
                'required_permissions': ['products:read']
            },
            {
                'key': 'blog',
                'label': 'Blog Posts',
                'icon': 'fas fa-newspaper',
                'component_name': 'BlogManagement',
                'path': '/admin/blog',
                'description': 'Create and manage blog content',
                'section': 'Main',
                'order': 3,
                'required_permissions': ['blog:read']
            },
            {
                'key': 'jobs',
                'label': 'Job Management',
                'icon': 'fas fa-briefcase',
                'component_name': 'JobManagement',
                'path': '/admin/jobs',
                'description': 'Post and manage job openings',
                'section': 'Main',
                'order': 4,
                'required_permissions': ['jobs:read']
            },
            {
                'key': 'outlets',
                'label': 'Outlet Locations',
                'icon': 'fas fa-map-marker-alt',
                'component_name': 'OutletManagement',
                'path': '/admin/outlets',
                'description': 'Manage physical locations',
                'section': 'Main',
                'order': 5,
                'required_permissions': ['outlets:read']
            },
            {
                'key': 'users',
                'label': 'User Management',
                'icon': 'fas fa-users',
                'component_name': 'UserManagement',
                'path': '/admin/users',
                'description': 'Manage system users',
                'section': 'Administration',
                'order': 1,
                'required_permissions': ['users:read']
            },
            {
                'key': 'tours',
                'label': 'Tour Bookings',
                'icon': 'fas fa-factory',
                'component_name': 'TourManagerBookings',
                'path': '/admin/tours',
                'description': 'Manage tour bookings',
                'section': 'Tours',
                'order': 1,
                'required_permissions': ['bookings:read']
            },
            {
                'key': 'tour-packages',
                'label': 'Tour Packages',
                'icon': 'fas fa-tag',
                'component_name': 'TourManagerPackages',
                'path': '/admin/tour-packages',
                'description': 'Manage tour packages & pricing',
                'section': 'Tours',
                'order': 2,
                'required_permissions': ['tours:read']
            },
            {
                'key': 'tour-calendar',
                'label': 'Tour Calendar',
                'icon': 'fas fa-calendar-alt',
                'component_name': 'TourManagerCalendar',
                'path': '/admin/tour-calendar',
                'description': 'Manage availability & schedule',
                'section': 'Tours',
                'order': 3,
                'required_permissions': ['tours:read']
            },
            {
                'key': 'permissions',
                'label': 'Permissions',
                'icon': 'fas fa-lock',
                'component_name': 'PermissionManager',
                'path': '/admin/permissions',
                'description': 'Manage user permissions',
                'section': 'Administration',
                'order': 2,
                'required_permissions': ['permissions:read']
            },
            {
                'key': 'roles',
                'label': 'Role Management',
                'icon': 'fas fa-user-tag',
                'component_name': 'RoleManager',
                'path': '/admin/roles',
                'description': 'Create and manage roles',
                'section': 'Administration',
                'order': 3
            },
            {
                'key': 'tour-staff',
                'label': 'Tour Staff',
                'icon': 'fas fa-users-cog',
                'component_name': 'TourStaffManagement',
                'path': '/admin/tour-staff',
                'description': 'Manage tour managers & assistants',
                'section': 'Tours',
                'order': 4
            },
            {
                'key': 'statistics',
                'label': 'Analytics',
                'icon': 'fas fa-chart-line',
                'component_name': 'AdvancedAnalytics',
                'path': '/admin/statistics',
                'description': 'Comprehensive analytics and insights',
                'section': 'Main',
                'order': 6,
                'required_permissions': ['statistics:read']
            },
            {
                'key': 'contacts',
                'label': 'Contact Messages',
                'icon': 'fas fa-envelope',
                'component_name': 'ContactManagement',
                'path': '/admin/contacts',
                'description': 'View and respond to customer inquiries',
                'section': 'Main',
                'order': 7,
                'required_permissions': ['contacts:read']
            },
            {
                'key': 'newsletter',
                'label': 'Newsletter',
                'icon': 'fas fa-envelope-open-text',
                'component_name': 'NewsletterManagement',
                'path': '/admin/newsletter',
                'description': 'Manage subscribers and send email campaigns',
                'section': 'Main',
                'order': 8,
                'required_permissions': ['newsletter:read']
            }
        ]
        
        components = {}
        for comp_data in default_components:
            comp = DashboardComponent(**comp_data)
            db.session.add(comp)
            db.session.flush()
            components[comp_data['key']] = comp
            logger.info(f"  ✅ Created component: {comp_data['key']}")
        
        db.session.commit()
        
        # ============ ASSIGN COMPONENTS TO ROLES ============
        logger.info("📦 Assigning components to roles...")
        
        role_assignments = {
            'super_admin': [
                'overview', 'products', 'blog', 'jobs', 'outlets', 'statistics', 'contacts', 'newsletter',
                'users', 'tours', 'tour-packages', 'tour-calendar', 'tour-staff',
                'permissions', 'roles'
            ],
            'admin': [
                'overview', 'products', 'blog', 'jobs', 'outlets', 'statistics', 'contacts', 'newsletter',
                'tours', 'tour-packages', 'tour-calendar', 'tour-staff'
            ],
            'tour_manager': [
                'overview', 'tours', 'tour-packages', 'tour-calendar', 'tour-staff', 'statistics'
            ],
            'tour_assistant': [
                'overview', 'tours', 'statistics'
            ],
            'partner': [
                'overview'
            ]
        }
        
        for role_name, component_keys in role_assignments.items():
            role = Role.query.filter_by(name=role_name).first()
            if role:
                for idx, key in enumerate(component_keys):
                    comp = DashboardComponent.query.filter_by(key=key).first()
                    if comp:
                        # Check if assignment already exists
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
                logger.info(f"  ✅ Assigned {len(component_keys)} components to {role_name}")
        
        db.session.commit()
        
        # ============ UPDATE EXISTING USERS ============
        logger.info("📦 Updating existing users with role assignments...")
        
        # Map existing role strings to role IDs
        role_map = {
            'super_admin': Role.query.filter_by(name='super_admin').first(),
            'admin': Role.query.filter_by(name='admin').first(),
            'tour_manager': Role.query.filter_by(name='tour_manager').first(),
            'tour_assistant': Role.query.filter_by(name='tour_assistant').first(),
            'partner': Role.query.filter_by(name='partner').first()
        }
        
        # Update users who have a role string but no role_id
        users = User.query.filter(User.role.isnot(None)).all()
        updated_count = 0
        for user in users:
            if user.role in role_map and user.role_id is None:
                role = role_map[user.role]
                if role:
                    user.role_id = role.id
                    updated_count += 1
        
        db.session.commit()
        logger.info(f"  ✅ Updated {updated_count} users with role IDs")
        
        logger.info("🎉 Dynamic roles migration completed successfully!")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Migration failed: {str(e)}")
        raise e


def downgrade():
    """Rollback the migration (drop tables)"""
    try:
        logger.info("⚠️ Rolling back dynamic roles migration...")
        
        from models import RoleComponent, DashboardComponent, Role, User
        
        # Remove role_id from users
        db.session.execute('ALTER TABLE users DROP COLUMN IF EXISTS role_id')
        
        # Drop tables in correct order
        db.session.execute('DROP TABLE IF EXISTS role_components CASCADE')
        db.session.execute('DROP TABLE IF EXISTS dashboard_components CASCADE')
        db.session.execute('DROP TABLE IF EXISTS roles CASCADE')
        
        db.session.commit()
        logger.info("✅ Migration rolled back successfully!")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Rollback failed: {str(e)}")
        raise e


# ============ RUN MIGRATION ============
if __name__ == '__main__':
    # This allows running the migration directly
    from app import create_app
    app = create_app()
    with app.app_context():
        upgrade()