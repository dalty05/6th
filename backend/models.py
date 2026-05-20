from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # Fresh Milk, Yoghurt, Lala, Ghee
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300))
    benefits = db.Column(db.Text)  # Key benefits/qualities
    packaging_sizes = db.Column(db.String(200))  # e.g., "500ml, 1L, 2L"
    nutritional_info = db.Column(db.Text)  # Optional nutritional facts
    ingredients = db.Column(db.Text)  # Ingredients list
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    excerpt = db.Column(db.String(300))
    content = db.Column(db.Text, nullable=False)
    featured_image = db.Column(db.String(300))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    views = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='published')  # draft, published
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    author = db.relationship('User', backref='posts')

class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    role = db.Column(db.String(100))  # director, trader, business woman, etc.
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)  # 1-5 stars
    is_approved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Statistic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100))  # "Our Farmers", "Cooperative Societies", etc.
    value = db.Column(db.String(50))  # "120,000+"
    suffix = db.Column(db.String(20))  # "+", "", etc.
    order = db.Column(db.Integer, default=0)