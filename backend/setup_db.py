# setup_db.py - Standalone database setup script
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime

# Create a minimal Flask app for database setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meru_dairy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define models directly in setup script
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='admin')
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300))
    benefits = db.Column(db.Text)
    packaging_sizes = db.Column(db.String(200))
    nutritional_info = db.Column(db.Text)
    ingredients = db.Column(db.Text)
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    excerpt = db.Column(db.String(300))
    content = db.Column(db.Text, nullable=False)
    featured_image = db.Column(db.String(300))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    views = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='published')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Testimonial(db.Model):
    __tablename__ = 'testimonials'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    role = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)
    is_approved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Statistic(db.Model):
    __tablename__ = 'statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100))
    value = db.Column(db.String(50))
    suffix = db.Column(db.String(20))
    order = db.Column(db.Integer, default=0)

class OTP(db.Model):
    __tablename__ = 'otp_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    email = db.Column(db.String(120), nullable=False)
    ip_address = db.Column(db.String(50))
    success = db.Column(db.Boolean, default=False)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)

class EmailVerificationToken(db.Model):
    __tablename__ = 'email_verification_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Run the setup
with app.app_context():
    # Drop all tables (comment out if you want to keep existing data)
    print("Dropping existing tables...")
    db.drop_all()
    
    # Create all tables
    print("Creating tables...")
    db.create_all()
    print("✅ All tables created successfully!")
    
    # Create super admin
    print("Creating super admin...")
    admin = User(
        email='admin@merudairy.co.ke',
        full_name='Super Administrator',
        role='super_admin',
        is_approved=True,
        is_active=True
    )
    admin.set_password('Admin123!')
    db.session.add(admin)
    
    # Create sample statistics
    print("Creating sample statistics...")
    stats = [
        Statistic(label='Our Farmers', value='120,000', suffix='+', order=1),
        Statistic(label='Cooperative Societies', value='120', suffix='+', order=2),
        Statistic(label='Litres of Milk Processed per day', value='600,000', suffix='+', order=3),
        Statistic(label='Customers Served', value='10,000,000', suffix='+', order=4)
    ]
    for stat in stats:
        db.session.add(stat)
    
    # Create sample products
    print("Creating sample products...")
    products = [
        Product(
            name='Mount Kenya Fresh Milk',
            category='Fresh Milk',
            description='Pure, fresh milk from the slopes of Mount Kenya. Pasteurized and packed fresh daily.',
            benefits='Rich in calcium and protein, supports bone health',
            packaging_sizes='500ml, 1L, 2L',
            featured=True
        ),
        Product(
            name='Mount Kenya Yoghurt',
            category='Yoghurt',
            description='Creamy, delicious yoghurt made from fresh milk. Available in multiple flavors.',
            benefits='Contains probiotics for gut health',
            packaging_sizes='200ml, 500ml, 1L',
            featured=True
        ),
        Product(
            name='Mount Kenya Lala',
            category='Lala',
            description='Traditional fermented milk drink, rich and tangy.',
            benefits='Natural probiotics, aids digestion',
            packaging_sizes='500ml, 1L',
            featured=True
        ),
        Product(
            name='Mount Kenya Ghee',
            category='Ghee',
            description='Pure clarified butter, perfect for cooking and traditional dishes.',
            benefits='Lactose-free, high smoke point for cooking',
            packaging_sizes='500g, 1kg',
            featured=True
        )
    ]
    for product in products:
        db.session.add(product)
    
    # Create sample testimonials
    print("Creating sample testimonials...")
    testimonials = [
        Testimonial(
            name='John M.',
            role='Director',
            content='Mount Kenya Milk has transformed our school feeding program. The quality is consistently excellent.',
            rating=5,
            is_approved=True
        ),
        Testimonial(
            name='Sarah W.',
            role='Trader',
            content='My customers love Mount Kenya products. The yoghurt is especially popular!',
            rating=5,
            is_approved=True
        ),
        Testimonial(
            name='Grace K.',
            role='Business Woman',
            content='I trust Mount Kenya Milk for my family. The quality is unmatched.',
            rating=5,
            is_approved=True
        )
    ]
    for testimonial in testimonials:
        db.session.add(testimonial)
    
    # Commit all changes
    db.session.commit()
    
    print("\n" + "=" * 50)
    print("✅ DATABASE SETUP COMPLETE!")
    print("=" * 50)
    print("\n📊 Tables created:")
    print("   - users")
    print("   - products")
    print("   - blog_posts")
    print("   - testimonials")
    print("   - statistics")
    print("   - otp_codes")
    print("   - password_reset_tokens")
    print("   - login_attempts")
    print("   - email_verification_tokens")
    print("")
    print("👤 SUPER ADMIN CREDENTIALS:")
    print("   Email: admin@merudairy.co.ke")
    print("   Password: Admin123!")
    print("")
    print("📦 Sample data created:")
    print(f"   - {len(products)} products")
    print(f"   - {len(stats)} statistics")
    print(f"   - {len(testimonials)} testimonials")
    print("=" * 50)