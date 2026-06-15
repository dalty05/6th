# backend/fix_settings.py
from app import app, db
from sqlalchemy import text

def fix_settings_table():
    with app.app_context():
        print("=" * 50)
        print("FIXING SYSTEM SETTINGS TABLE")
        print("=" * 50)
        
        # Check if table exists
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'system_settings' in tables:
            print("Table 'system_settings' exists. Checking columns...")
            
            # Get existing columns
            columns = [col['name'] for col in inspector.get_columns('system_settings')]
            print(f"Existing columns: {columns}")
            
            # Add missing columns
            if 'updated_by' not in columns:
                try:
                    db.session.execute(text("ALTER TABLE system_settings ADD COLUMN updated_by INTEGER"))
                    db.session.commit()
                    print("✅ Added 'updated_by' column")
                except Exception as e:
                    print(f"Error adding column: {e}")
            
            # Clear existing data (optional - comment out if you want to keep data)
            # db.session.execute(text("DELETE FROM system_settings"))
            # db.session.commit()
            # print("✅ Cleared existing settings")
            
        else:
            print("Table 'system_settings' does not exist. Creating...")
            db.create_all()
            print("✅ Table created")
        
        # Initialize default settings
        print("\n📝 Initializing default settings...")
        
        try:
            from settings_routes import DEFAULT_SETTINGS, set_setting
            
            # Clear existing to avoid duplicates
            db.session.execute(text("DELETE FROM system_settings"))
            db.session.commit()
            
            for group, settings_data in DEFAULT_SETTINGS.items():
                for key, value in settings_data.items():
                    set_setting(key, value, group)
                    print(f"   ✓ {group}.{key} = {value}")
            
            # Generate API key
            import secrets
            api_key = secrets.token_urlsafe(32)
            set_setting('api_key', api_key, 'api')
            print(f"   ✓ api.api_key = {api_key}")
            
            print("\n✅ Default settings initialized!")
            
        except Exception as e:
            print(f"Error initializing settings: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 50)
        print("FIX COMPLETE")
        print("=" * 50)

if __name__ == '__main__':
    fix_settings_table()