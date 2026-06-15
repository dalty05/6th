"""
Complete Database Setup with Migrations
Run with: python full_migration.py
"""

import sqlite3
import os
from app import app, db
from models import User, Product, BlogPost, Testimonial, Statistic, NewsletterSubscriber
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_tables():
    """Create all database tables"""
    with app.app_context():
        print("📋 Creating database tables...")
        db.create_all()
        print("✅ Tables created successfully!")
        return True

def add_missing_columns():
    """Add soft delete columns to existing tables"""
    db_path = 'meru_dairy.db'
    
    if not os.path.exists(db_path):
        print("⚠️ Database file not found, skipping column additions")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"📋 Found tables: {', '.join(tables)}")
    
    # Define columns to add for each table
    migrations = {}
    
    if 'product' in tables:
        migrations['product'] = ['is_deleted', 'deleted_at', 'deleted_by']
    
    if 'blog_post' in tables:
        migrations['blog_post'] = ['is_deleted', 'deleted_at', 'deleted_by']
    
    if 'testimonial' in tables:
        migrations['testimonial'] = ['is_deleted', 'deleted_at', 'deleted_by']
    
    if 'users' in tables:
        migrations['users'] = ['is_active', 'phone', 'last_login', 'two_factor_enabled', 'two_factor_secret']
    
    for table_name, columns in migrations.items():
        try:
            # Get existing columns
            cursor.execute(f"PRAGMA table_info({table_name})")
            existing = [col[1] for col in cursor.fetchall()]
            
            # Add missing columns
            for col_name in columns:
                if col_name not in existing:
                    try:
                        if col_name in ['is_deleted', 'is_active', 'two_factor_enabled']:
                            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} BOOLEAN DEFAULT 0")
                        elif col_name in ['deleted_at', 'last_login']:
                            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} DATETIME")
                        elif col_name in ['deleted_by']:
                            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} INTEGER")
                        elif col_name in ['phone']:
                            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} VARCHAR(20)")
                        elif col_name in ['two_factor_secret']:
                            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} VARCHAR(255)")
                        print(f"  ✅ Added {col_name} to {table_name}")
                    except sqlite3.Error as e:
                        print(f"  ⚠️ Could not add {col_name} to {table_name}: {e}")
        except Exception as e:
            print(f"Error processing {table_name}: {e}")
    
    conn.commit()
    conn.close()

def add_sample_data():
    """Add initial sample data if tables are empty"""
    with app.app_context():
        # Check if we're using email or username for login
        from models import User
        
        # Try to find by email first (most common)
        admin = None
        try:
            admin = User.query.filter_by(email='admin@merudairy.co.ke').first()
        except:
            pass
        
        if not admin:
            try:
                admin = User.query.filter_by(full_name='Administrator').first()
            except:
                pass
        
        # Create admin user if not exists
        if not admin:
            print("\n👤 Creating admin user...")
            try:
                # Check what fields the User model has
                user_columns = [col.name for col in User.__table__.columns]
                print(f"📋 User model fields: {user_columns}")
                
                # Create user based on available fields
                admin = User()
                
                # Set fields if they exist
                if 'email' in user_columns:
                    admin.email = 'admin@merudairy.co.ke'
                if 'full_name' in user_columns:
                    admin.full_name = 'Administrator'
                if 'role' in user_columns:
                    admin.role = 'super_admin'
                if 'is_active' in user_columns:
                    admin.is_active = True
                
                # Set password
                admin.set_password('admin123')
                
                db.session.add(admin)
                db.session.commit()
                print("  ✅ Admin user created!")
                print("  🔑 Login with email: admin@merudairy.co.ke")
                print("  🔑 Password: admin123")
            except Exception as e:
                print(f"  ❌ Error creating admin: {e}")
                db.session.rollback()
        else:
            print("\n✅ Admin user already exists")
        
        # Add statistics
        try:
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
                db.session.commit()
                print("  ✅ Statistics added")
            else:
                print(f"\n📊 Statistics already exist: {Statistic.query.count()} records")
        except Exception as e:
            print(f"Error adding statistics: {e}")
        
        # Add testimonials
        try:
            if Testimonial.query.count() == 0:
                print("\n💬 Adding testimonials...")
                testimonials = [
                    Testimonial(name='John M.', role='Director', content='Mount Kenya Milk has transformed our dairy business. The quality is consistently excellent!', rating=5, is_approved=True),
                    Testimonial(name='Sarah W.', role='Trader', content='My customers love the fresh taste of Mount Kenya Yoghurt. It sells out every day!', rating=5, is_approved=True),
                    Testimonial(name='Peter K.', role='Business Owner', content='The cooperative model ensures farmers get fair prices while consumers get premium quality.', rating=4, is_approved=True)
                ]
                for testimonial in testimonials:
                    db.session.add(testimonial)
                db.session.commit()
                print("  ✅ Testimonials added")
            else:
                print(f"\n💬 Testimonials already exist: {Testimonial.query.count()} records")
        except Exception as e:
            print(f"Error adding testimonials: {e}")
        
        # Add products
        try:
            if Product.query.count() == 0:
                print("\n🥛 Adding products...")
                products = [
                    Product(
                        name='Mount Kenya Fresh Milk',
                        category='Fresh Milk',
                        description='Pure, fresh milk sourced directly from our cooperative farmers. Pasteurized and packed fresh daily to preserve all natural goodness.',
                        benefits='Rich in calcium and protein. Supports strong bones and healthy growth.',
                        packaging_sizes='500ml, 1L, 2L',
                        nutritional_info='Per 100ml: Energy 65kcal, Protein 3.2g, Fat 3.5g, Calcium 120mg',
                        ingredients='100% Fresh Cow Milk',
                        featured=True
                    ),
                    Product(
                        name='Mount Kenya Yoghurt',
                        category='Yoghurt',
                        description='Creamy, delicious yoghurt made from fresh Mount Kenya milk. Available in various flavors.',
                        benefits='Probiotic rich, aids digestion. Great source of protein and calcium.',
                        packaging_sizes='200ml, 500ml, 1L',
                        nutritional_info='Per 100g: Energy 85kcal, Protein 3.5g, Fat 3.0g, Calcium 150mg',
                        ingredients='Fresh Milk, Live Yoghurt Cultures',
                        featured=True
                    ),
                    Product(
                        name='Mount Kenya Lala',
                        category='Lala',
                        description='Traditional fermented milk with a rich, tangy taste. A Kenyan favorite.',
                        benefits='Natural probiotics for gut health. Rich in B vitamins.',
                        packaging_sizes='500ml, 1L',
                        nutritional_info='Per 100ml: Energy 70kcal, Protein 3.0g, Fat 3.2g',
                        ingredients='Fermented Cow Milk',
                        featured=True
                    ),
                    Product(
                        name='Mount Kenya Ghee',
                        category='Ghee',
                        description='Pure clarified butter made from premium Mount Kenya milk. Perfect for cooking and traditional dishes.',
                        benefits='Lactose-free, high smoke point for cooking. Rich in healthy fats.',
                        packaging_sizes='200g, 500g, 1kg',
                        nutritional_info='Per 100g: Energy 900kcal, Fat 100g',
                        ingredients='100% Pure Cow Milk Butter',
                        featured=True
                    )
                ]
                for product in products:
                    db.session.add(product)
                db.session.commit()
                print("  ✅ Products added")
            else:
                print(f"\n🥛 Products already exist: {Product.query.count()} records")
        except Exception as e:
            print(f"Error adding products: {e}")
        
        # Add blog posts
        try:
            # Get admin user ID for author
            admin_user = User.query.first()
            admin_id = admin_user.id if admin_user else 1
            
            if BlogPost.query.count() == 0:
                print("\n📝 Adding blog posts...")
                posts = [
                    BlogPost(
                        title='The Journey of Mount Kenya Milk: From Farm to Table',
                        slug='journey-of-mount-kenya-milk',
                        excerpt='Discover how our cooperative ensures the highest quality milk from our farmers to your family.',
                        content='At Meru Central Dairy Co-operative Union, we take pride in our farm-to-table approach. Our journey begins with over 120,000 dedicated farmers who care for their cattle using traditional and modern sustainable practices.\n\nThe milk is collected twice daily from our network of cooperative societies, ensuring freshness. We use state-of-the-art processing facilities to maintain quality while preserving natural goodness.',
                        status='published',
                        author_id=admin_id
                    ),
                    BlogPost(
                        title='5 Benefits of Traditional Fermented Milk (Lala)',
                        slug='benefits-of-fermented-milk-lala',
                        excerpt='Explore the health benefits and cultural significance of Lala, a traditional Kenyan delicacy.',
                        content='Lala, also known as fermented milk, has been a staple in Kenyan households for generations. Beyond its delicious tangy taste, it offers numerous health benefits.\n\n1. Improves Digestion\n2. Boosts Immunity\n3. Rich in Probiotics\n4. Lactose-Friendly\n5. Preserves Naturally',
                        status='published',
                        author_id=admin_id
                    ),
                    BlogPost(
                        title='Supporting Our Farmers: The Cooperative Difference',
                        slug='supporting-our-farmers-cooperative',
                        excerpt='Learn how our cooperative model empowers farmers and strengthens our community.',
                        content='At Meru Dairy, we believe in fair trade and supporting our farming community. Our cooperative model ensures:\n\n• Fair prices for quality milk\n• Access to veterinary services\n• Training on modern farming techniques\n• Community development programs\n\nThis approach has helped us become Kenya\'s largest dairy cooperative.',
                        status='published',
                        author_id=admin_id
                    )
                ]
                for post in posts:
                    db.session.add(post)
                db.session.commit()
                print("  ✅ Blog posts added")
            else:
                print(f"\n📝 Blog posts already exist: {BlogPost.query.count()} records")
        except Exception as e:
            print(f"Error adding blog posts: {e}")

def run_full_migration():
    """Run complete database setup"""
    print("=" * 60)
    print("COMPLETE DATABASE SETUP")
    print("=" * 60)
    
    print("\n🔨 Step 1: Creating tables...")
    create_tables()
    
    print("\n🔧 Step 2: Adding missing columns...")
    add_missing_columns()
    
    print("\n📦 Step 3: Adding sample data...")
    add_sample_data()
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print("\nYou can now:")
    print("  1. Run: python app.py")
    print("  2. Login with: admin@merudairy.co.ke / admin123")
    print("\n⚠️ Don't forget to create an 'uploads' folder for images!")

if __name__ == '__main__':
    # Create uploads folder
    os.makedirs('uploads/products', exist_ok=True)
    os.makedirs('uploads/blogs', exist_ok=True)
    os.makedirs('uploads/general', exist_ok=True)
    
    run_full_migration()