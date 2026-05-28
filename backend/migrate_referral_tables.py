# backend/migrate_referral_tables.py
from app import app, db
from models import ActivityLog, ReferralLink, ReferralClick

with app.app_context():
    # Create new tables
    db.create_all()
    print("✅ Referral and Activity tables created/verified")
    
    # Check if tables exist
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    
    print("\n📊 Tables in database:")
    for table in tables:
        print(f"   - {table}")