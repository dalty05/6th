

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import inspect, text
from datetime import datetime

def add_columns():
    """Add tour columns to users table if they don't exist"""
    with app.app_context():
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        added = []
        
        if 'is_tour_manager' not in columns:
            print("➕ Adding is_tour_manager column to users table...")
            db.session.execute(text(
                "ALTER TABLE users ADD COLUMN is_tour_manager BOOLEAN DEFAULT 0"
            ))
            added.append('is_tour_manager')
        
        if 'is_tour_assistant' not in columns:
            print("➕ Adding is_tour_assistant column to users table...")
            db.session.execute(text(
                "ALTER TABLE users ADD COLUMN is_tour_assistant BOOLEAN DEFAULT 0"
            ))
            added.append('is_tour_assistant')
        
        if added:
            print(f"✅ Added columns: {', '.join(added)}")
        else:
            print("✅ All tour columns already exist in users table")
        
        db.session.commit()

def create_tour_tables():
    """Create tour tables if they don't exist"""
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        tables_to_create = [
            'tour_packages',
            'tour_bookings',
            'tour_availability',
            'tour_payments',
            'tour_invoices'
        ]
        
        created = []
        for table in tables_to_create:
            if table not in existing_tables:
                print(f"📦 Creating table: {table}")
                created.append(table)
        
        if created:
            db.create_all()
            print(f"✅ Created tables: {', '.join(created)}")
        else:
            print("✅ All tour tables already exist")

def add_sample_packages():
    """Add sample tour packages if none exist"""
    with app.app_context():
        from models import TourPackage
        
        existing = TourPackage.query.count()
        if existing > 0:
            print(f"✅ {existing} packages already exist, skipping sample data")
            return
        
        print("📦 Adding sample tour packages...")
        
        packages = [
            {
                'name': 'Standard Factory Tour',
                'slug': 'standard-factory-tour',
                'description': 'Experience the complete dairy production process from milking to packaging. This 2-hour guided tour takes you through our state-of-the-art facility.',
                'short_description': '2-hour guided tour of our entire production facility',
                'base_price': 1500.00,
                'min_people': 1,
                'max_people': 300,
                'duration_hours': 2,
                'includes': ['Factory tour guide', 'Product tasting', 'Safety gear', 'Certificate of participation'],
                'excludes': ['Transport to factory', 'Meals'],
                'is_active': True,
                'is_featured': True
            },
            {
                'name': 'Premium Farm-to-Table Experience',
                'slug': 'premium-farm-to-table',
                'description': 'Full day experience including farm visit, factory tour, and gourmet lunch. Get hands-on experience with our farming and production processes.',
                'short_description': 'Complete 6-hour experience from farm to table',
                'base_price': 3500.00,
                'min_people': 2,
                'max_people': 300,
                'duration_hours': 6,
                'includes': ['Farm visit', 'Factory tour', 'Gourmet lunch', 'Product tasting', 'Certificate', 'Transport within factory'],
                'excludes': ['Transport to factory'],
                'is_active': True,
                'is_featured': True
            },
            {
                'name': 'School Educational Tour',
                'slug': 'school-educational-tour',
                'description': 'Specially designed for school groups with educational content and activities. Perfect for students learning about agriculture and food production.',
                'short_description': 'Educational 3-hour tour for schools and students',
                'base_price': 800.00,
                'min_people': 10,
                'max_people': 300,
                'duration_hours': 3,
                'includes': ['Educational guide', 'Interactive activities', 'Product samples', 'Educational materials', 'Safety gear'],
                'excludes': ['Transport to factory', 'Meals'],
                'is_active': True,
                'is_featured': True
            }
        ]
        
        for pkg_data in packages:
            package = TourPackage(**pkg_data)
            db.session.add(package)
        
        db.session.commit()
        print(f"✅ Added {len(packages)} sample packages!")

def verify_migration():
    """Verify the migration was successful"""
    with app.app_context():
        inspector = inspect(db.engine)
        
        print("\n📋 Verification:")
        print("-" * 40)
        
        # Check users table columns
        columns = [col['name'] for col in inspector.get_columns('users')]
        tour_cols = ['is_tour_manager', 'is_tour_assistant']
        print(f"Users table - Tour columns: {', '.join([c for c in tour_cols if c in columns])}")
        
        # Check tour tables
        tables = inspector.get_table_names()
        tour_tables = ['tour_packages', 'tour_bookings', 'tour_availability', 'tour_payments', 'tour_invoices']
        existing = [t for t in tour_tables if t in tables]
        print(f"Tour tables: {', '.join(existing) if existing else 'None'}")
        
        # Check packages
        from models import TourPackage
        count = TourPackage.query.count()
        print(f"Sample packages: {count}")
        print("-" * 40)

def run_migration():
    """Run the complete migration"""
    print("=" * 50)
    print("🚀 STARTING TOUR SYSTEM MIGRATION")
    print("=" * 50)
    
    try:
        print("\n📌 Step 1: Adding tour columns to users table...")
        add_columns()
        
        print("\n📌 Step 2: Creating tour tables...")
        create_tour_tables()
        
        print("\n📌 Step 3: Adding sample packages...")
        add_sample_packages()
        
        print("\n📌 Step 4: Verifying migration...")
        verify_migration()
        
        print("\n✅ Migration completed successfully!")
        print("=" * 50)
        print("\n🎯 What was added:")
        print("  - is_tour_manager (boolean) to users table")
        print("  - is_tour_assistant (boolean) to users table")
        print("  - tour_packages table")
        print("  - tour_bookings table")
        print("  - tour_availability table")
        print("  - tour_payments table")
        print("  - tour_invoices table")
        print("  - 3 sample tour packages")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        db.session.rollback()
        sys.exit(1)

if __name__ == "__main__":
    run_migration()