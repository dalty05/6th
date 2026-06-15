# backend/migrate_settings.py
from app import app, db
from models import SystemSetting

def migrate_settings():
    with app.app_context():
        # Create settings table
        db.create_all()
        print("✅ Settings table verified")
        
        # Check if settings exist
        if SystemSetting.query.count() == 0:
            print("📝 Initializing default settings...")
            
            from settings_routes import DEFAULT_SETTINGS, set_setting
            import secrets
            
            for group, settings_data in DEFAULT_SETTINGS.items():
                for key, value in settings_data.items():
                    set_setting(key, value, group)
                    print(f"   ✓ {group}.{key} = {value}")
            
            # Generate API key
            api_key = secrets.token_urlsafe(32)
            set_setting('api_key', api_key, 'api')
            print(f"   ✓ api.api_key = {api_key}")
            
            print("\n✅ Default settings initialized!")
        else:
            print(f"📋 Settings already exist ({SystemSetting.query.count()} records)")

if __name__ == '__main__':
    migrate_settings()