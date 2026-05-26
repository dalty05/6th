from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
import secrets
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='admin')  # super_admin, admin, viewer
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - define after all columns
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_super_admin(self):
        return self.role == 'super_admin'
    
    def can_manage_users(self):
        return self.role in ['super_admin', 'admin']
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'is_approved': self.is_approved,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class OTP(db.Model):
    __tablename__ = 'otp_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def generate_otp():
        return str(secrets.randbelow(1000000)).zfill(6)
    
    def is_valid(self):
        return not self.is_verified and datetime.utcnow() < self.expires_at

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(32)
    
    def is_valid(self):
        return not self.used and datetime.utcnow() < self.expires_at

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
    
    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(32)
    
    def is_valid(self):
        return not self.used and datetime.utcnow() < self.expires_at

# Product model (keep your existing one)
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

# class BlogPost(db.Model):
#     __tablename__ = 'blog_posts'
    
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(200), nullable=False)
#     slug = db.Column(db.String(200), unique=True, nullable=False)
#     excerpt = db.Column(db.String(300))
#     content = db.Column(db.Text, nullable=False)
#     featured_image = db.Column(db.String(300))
#     author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     views = db.Column(db.Integer, default=0)
#     status = db.Column(db.String(20), default='published')
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
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

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'excerpt': self.excerpt,
            'content': self.content,
            'featured_image': self.featured_image,
            'author': self.author.full_name if self.author else 'Admin',
            'views': self.views,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }





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

# Add relationships after all models are defined
User.approved_by = db.relationship('User', remote_side=[User.id], foreign_keys=[User.approved_by_id])
User.otp_codes = db.relationship('OTP', backref='user', lazy='dynamic', cascade='all, delete-orphan')
User.password_resets = db.relationship('PasswordResetToken', backref='user', lazy='dynamic', cascade='all, delete-orphan')
User.login_attempts = db.relationship('LoginAttempt', backref='user', lazy='dynamic', cascade='all, delete-orphan')
User.email_verifications = db.relationship('EmailVerificationToken', backref='user', lazy='dynamic', cascade='all, delete-orphan')
User.blog_posts = db.relationship('BlogPost', backref='author', lazy='dynamic')