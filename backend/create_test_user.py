#!/usr/bin/env python
"""Create a test admin user for testing"""

from app import app, db
from models import User

with app.app_context():
    # Check if user already exists
    existing = User.query.filter_by(email='admin@merudairy.co.ke').first()
    if existing:
        print(f"✓ User already exists: {existing.email}")
    else:
        # Create first user (will be super_admin)
        user = User(
            email='admin@merudairy.co.ke',
            full_name='Test Admin',
            role='super_admin',
            is_active=True,
            is_approved=True,
            email_verified=True
        )
        user.set_password('Admin123456')
        
        db.session.add(user)
        db.session.commit()
        
        print(f"✓ Created test user:")
        print(f"  Email: admin@merudairy.co.ke")
        print(f"  Password: Admin123456")
        print(f"  Role: super_admin")
        print(f"\nYou can now login with these credentials!")
