#!/usr/bin/env python
"""Create a test admin user for testing"""

from app import app, db
from models import User

with app.app_context():
    # Check if user already exists
    existing = User.query.filter_by(email='oyigodalton@gmail.com').first()
    if existing:
        print(f"✓ User already exists: {existing.email}")
    else:
        # Create first user (will be super_admin)
        user = User(
            email='oyigodalton@gmail.com',
            full_name='Dalton Oyigo',
            role='super_admin',
            is_active=True,
            is_approved=True,
            email_verified=True
        )
        user.set_password('Admin123!')
        
        db.session.add(user)
        db.session.commit()
        
        print(f"✓ Created test user:")
        print(f"  Email: oyigodalton@gmail.com")
        print(f"  Password: Admin123!")
        print(f"  Role: super_admin")
        print(f"\nYou can now login with these credentials!")
