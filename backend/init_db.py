from app import app, db
from models import User, Product, BlogPost, Testimonial, Statistic, NewsletterSubscriber
from werkzeug.security import generate_password_hash

with app.app_context():
    print("=" * 50)
    print("CREATING DATABASE TABLES")
    print("=" * 50)
    
    # Create all tables
    db.create_all()
    print("✅ Tables created successfully!")
    
    # Verify tables
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"\n📋 Tables created: {', '.join(tables)}")
    
    # Create admin user if not exists
    admin = User.query.filter_by(email='admin@merudairy.co.ke').first()
    if not admin:
        print("\n👤 Creating admin user...")
        admin = User(
            email='admin@merudairy.co.ke',
            full_name='Administrator',
            role='super_admin',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print("  ✅ Admin: admin@merudairy.co.ke / admin123")
    else:
        print("\n✅ Admin user already exists")
    
    # Add sample statistics
    if Statistic.query.count() == 0:
        print("\n📊 Adding statistics...")
        stats = [
            Statistic(label='Our Farmers', value='120,000', suffix='+', order=1),
            Statistic(label='Cooperative Societies', value='120', suffix='+', order=2),
            Statistic(label='Litres of Milk Processed per day', value='600,000', suffix='+', order=3),
            Statistic(label='Customers Served', value='10,000,000', suffix='+', order=4)
        ]
        for stat in stats:
            db.session.add(stat)
        print("  ✅ Statistics added")
    else:
        print("\n📊 Statistics already exist")
    
    db.session.commit()
    
    print("\n" + "=" * 50)
    print("✅ DATABASE INITIALIZATION COMPLETE!")
    print("=" * 50)
    print("\nNext steps:")
    print("  1. Run: python app.py")
    print("  2. Login with: admin@merudairy.co.ke / admin123")


    