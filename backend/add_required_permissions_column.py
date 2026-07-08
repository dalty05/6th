# backend/add_missing_columns.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db
from sqlalchemy import text

with app.app_context():
    print("🔍 Adding missing columns to dashboard_components...")
    
    try:
        # Check existing columns
        result = db.session.execute(text("PRAGMA table_info(dashboard_components)"))
        existing_columns = [row[1] for row in result]
        
        print(f"📋 Existing columns: {', '.join(existing_columns)}")
        
        # Columns to add
        columns_to_add = {
            'created_at': 'DATETIME',
            'updated_at': 'DATETIME',
            'required_permissions': "TEXT DEFAULT '[]'"
        }
        
        added_count = 0
        for col_name, col_type in columns_to_add.items():
            if col_name not in existing_columns:
                print(f"📋 Adding column: {col_name}")
                try:
                    db.session.execute(text(f"ALTER TABLE dashboard_components ADD COLUMN {col_name} {col_type}"))
                    added_count += 1
                except Exception as e:
                    print(f"   ⚠️ Error adding {col_name}: {e}")
            else:
                print(f"✅ {col_name} already exists")
        
        db.session.commit()
        print(f"✅ Added {added_count} missing columns")
        
        # Verify columns now exist
        result = db.session.execute(text("PRAGMA table_info(dashboard_components)"))
        columns = [row[1] for row in result]
        print(f"📋 Updated columns: {', '.join(columns)}")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")
    
    print("🎉 Done!")