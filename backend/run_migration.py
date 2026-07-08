# backend/add_role_id.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db
from sqlalchemy import text

with app.app_context():
    print("🔍 Adding role_id column to users table...")
    
    try:
        # Check if column exists
        result = db.session.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result]
        
        if 'role_id' in columns:
            print("✅ role_id column already exists!")
        else:
            # Add the column
            db.session.execute(text("ALTER TABLE users ADD COLUMN role_id INTEGER REFERENCES roles(id)"))
            db.session.commit()
            print("✅ role_id column added successfully!")
            
            # Update existing users with role_id
            print("🔄 Updating existing users with role IDs...")
            
            # Get role mappings
            roles = db.session.execute(text("SELECT id, name FROM roles")).fetchall()
            role_map = {name: id for id, name in roles}
            
            # Update users
            users = db.session.execute(text("SELECT id, role FROM users WHERE role IS NOT NULL")).fetchall()
            updated_count = 0
            for user_id, role_name in users:
                if role_name in role_map:
                    db.session.execute(
                        text("UPDATE users SET role_id = :role_id WHERE id = :user_id"),
                        {"role_id": role_map[role_name], "user_id": user_id}
                    )
                    updated_count += 1
            
            db.session.commit()
            print(f"✅ Updated {updated_count} users with role IDs")
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")
    
    print("🎉 Done!")