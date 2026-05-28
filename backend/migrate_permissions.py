# migrate_permissions.py
from app import app, db
from models import User, PermissionTemplate, ReferralLink, ReferralClick
import json

with app.app_context():
    # Create new tables
    db.create_all()
    
    print("✅ Permission tables created")
    
    # Update existing users with default permissions
    users = User.query.all()
    for user in users:
        if user.role != 'super_admin' and (not user.permissions or user.permissions == '{}'):
            default_perms = user.get_default_permissions()
            user.permissions = json.dumps(default_perms)
            print(f"  Updated permissions for {user.email}")
    
    # Generate referral codes for existing partners
    partners = User.query.filter_by(role='partner').all()
    for partner in partners:
        if not partner.referral_code:
            partner.generate_referral_code()
            print(f"  Generated referral code for {partner.email}: {partner.referral_code}")
    
    db.session.commit()
    
    print("\n" + "="*50)
    print("✅ PERMISSION SYSTEM MIGRATION COMPLETE")
    print("="*50)
    print("\nNew Features:")
    print("  - Granular permission system (CRUD per resource)")
    print("  - Partner referral tracking")
    print("  - User management by super admin only")
    print("="*50)