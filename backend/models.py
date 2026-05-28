from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
import secrets
import json
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    # Basic fields
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='partner')  # super_admin, admin, partner
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Partner specific fields
    referral_code = db.Column(db.String(50), unique=True)
    total_clicks = db.Column(db.Integer, default=0)
    total_conversions = db.Column(db.Integer, default=0)
    
    # Permission JSON field
    permissions = db.Column(db.Text, default='{}')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(50))
    
    # Relationships
    created_by = db.relationship('User', remote_side=[id], foreign_keys=[created_by_id])
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_super_admin(self):
        return self.role == 'super_admin'
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_partner(self):
        return self.role == 'partner'
    
    def get_permissions(self):
        """Get permissions as dictionary"""
        if self.permissions:
            try:
                return json.loads(self.permissions)
            except:
                return self.get_default_permissions()
        return self.get_default_permissions()
    
    def get_default_permissions(self):
        """Get default permissions based on role"""
        if self.role == 'super_admin':
            return {
                'products': {'create': True, 'read': True, 'update': True, 'delete': True},
                'blog': {'create': True, 'read': True, 'update': True, 'delete': True},
                'users': {'create': True, 'read': True, 'update': True, 'delete': True},
                'partners': {'create': True, 'read': True, 'update': True, 'delete': True},
                'referrals': {'create': True, 'read': True, 'update': True, 'delete': True},
                'statistics': {'create': True, 'read': True, 'update': True, 'delete': True},
                'settings': {'create': True, 'read': True, 'update': True, 'delete': True}
            }
        elif self.role == 'admin':
            return {
                'products': {'create': True, 'read': True, 'update': True, 'delete': False},
                'blog': {'create': True, 'read': True, 'update': True, 'delete': False},
                'users': {'create': False, 'read': True, 'update': False, 'delete': False},
                'partners': {'create': True, 'read': True, 'update': True, 'delete': False},
                'referrals': {'create': True, 'read': True, 'update': True, 'delete': False},
                'statistics': {'create': False, 'read': True, 'update': False, 'delete': False},
                'settings': {'create': False, 'read': False, 'update': False, 'delete': False}
            }
        else:  # partner
            return {
                'products': {'create': False, 'read': True, 'update': False, 'delete': False},
                'blog': {'create': False, 'read': True, 'update': False, 'delete': False},
                'users': {'create': False, 'read': False, 'update': False, 'delete': False},
                'partners': {'create': False, 'read': False, 'update': False, 'delete': False},
                'referrals': {'create': True, 'read': True, 'update': True, 'delete': False},
                'statistics': {'create': False, 'read': True, 'update': False, 'delete': False},
                'settings': {'create': False, 'read': False, 'update': False, 'delete': False}
            }
    
    def has_permission(self, resource, action):
        """Check if user has specific permission"""
        if self.role == 'super_admin':
            return True
        perms = self.get_permissions()
        return perms.get(resource, {}).get(action, False)
    
    def can_view(self, resource):
        return self.has_permission(resource, 'read')
    
    def can_create(self, resource):
        return self.has_permission(resource, 'create')
    
    def can_update(self, resource):
        return self.has_permission(resource, 'update')
    
    def can_delete(self, resource):
        return self.has_permission(resource, 'delete')
    
    def set_permission(self, resource, action, value):
        """Set specific permission for a user (super admin only)"""
        if self.role == 'super_admin':
            return False
        
        perms = self.get_permissions()
        if resource not in perms:
            perms[resource] = {'create': False, 'read': False, 'update': False, 'delete': False}
        perms[resource][action] = value
        self.permissions = json.dumps(perms)
        return True
    
    def set_permissions_bulk(self, permissions_dict):
        """Set multiple permissions at once"""
        if self.role == 'super_admin':
            return False
        self.permissions = json.dumps(permissions_dict)
        return True
    
    def generate_referral_code(self):
        """Generate unique referral code for partner"""
        import random
        import string
        code = f"PARTNER-{self.id}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        self.referral_code = code
        return code
    
    def to_dict(self, include_permissions=False):
        data = {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'is_approved': self.is_approved,
            'referral_code': self.referral_code,
            'total_clicks': self.total_clicks,
            'total_conversions': self.total_conversions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        if include_permissions:
            data['permissions'] = self.get_permissions()
        return data


class ReferralLink(db.Model):
    __tablename__ = 'referral_links'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    link_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    destination_url = db.Column(db.String(500))
    campaign_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    total_clicks = db.Column(db.Integer, default=0)
    unique_clicks = db.Column(db.Integer, default=0)
    conversions = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('referral_links', lazy='dynamic'))
    clicks = db.relationship('ReferralClick', backref='link', lazy='dynamic', cascade='all, delete-orphan')
    
    def generate_code(self):
        import random
        import string
        self.link_code = f"REF-{self.user_id}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
        return self.link_code
    
    def get_full_url(self, base_url):
        return f"{base_url}/r/{self.link_code}"
    
    def increment_click(self, ip_address, user_agent, referrer=None):
        click = ReferralClick(
            link_id=self.id,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer_url=referrer
        )
        db.session.add(click)
        self.total_clicks += 1
        
        # Check for unique click (same IP within 24 hours)
        recent_click = ReferralClick.query.filter(
            ReferralClick.link_id == self.id,
            ReferralClick.ip_address == ip_address,
            ReferralClick.clicked_at > datetime.utcnow() - timedelta(hours=24)
        ).first()
        
        if not recent_click:
            self.unique_clicks += 1
        
        # Update user total
        self.user.total_clicks += 1
        db.session.commit()
        return click
    
    def record_conversion(self):
        self.conversions += 1
        self.user.total_conversions += 1
        db.session.commit()
    
    def to_dict(self, base_url=None):
        data = {
            'id': self.id,
            'name': self.name,
            'link_code': self.link_code,
            'campaign_name': self.campaign_name,
            'is_active': self.is_active,
            'total_clicks': self.total_clicks,
            'unique_clicks': self.unique_clicks,
            'conversions': self.conversions,
            'conversion_rate': round((self.conversions / self.total_clicks * 100), 2) if self.total_clicks > 0 else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
        if base_url:
            data['url'] = self.get_full_url(base_url)
        return data


class ReferralClick(db.Model):
    __tablename__ = 'referral_clicks'
    
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('referral_links.id'), nullable=False)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    referrer_url = db.Column(db.String(500))
    converted = db.Column(db.Boolean, default=False)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'referrer_url': self.referrer_url,
            'converted': self.converted,
            'clicked_at': self.clicked_at.isoformat() if self.clicked_at else None
        }


class PermissionTemplate(db.Model):
    __tablename__ = 'permission_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def get_template(template_name):
        templates = {
            'partner_full': {
                'display_name': 'Partner - Full Access',
                'description': 'Can create and manage referral links, view all stats',
                'permissions': {
                    'products': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'blog': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'referrals': {'create': True, 'read': True, 'update': True, 'delete': False},
                    'statistics': {'create': False, 'read': True, 'update': False, 'delete': False}
                }
            },
            'partner_readonly': {
                'display_name': 'Partner - Read Only',
                'description': 'Can only view stats, cannot create or edit links',
                'permissions': {
                    'products': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'blog': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'referrals': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'statistics': {'create': False, 'read': True, 'update': False, 'delete': False}
                }
            },
            'partner_creator': {
                'display_name': 'Partner - Creator',
                'description': 'Can create, edit, and delete own referral links',
                'permissions': {
                    'products': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'blog': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'referrals': {'create': True, 'read': True, 'update': True, 'delete': True},
                    'statistics': {'create': False, 'read': True, 'update': False, 'delete': False}
                }
            },
            'admin_full': {
                'display_name': 'Admin - Full Access',
                'description': 'Full product and blog management, can view partners',
                'permissions': {
                    'products': {'create': True, 'read': True, 'update': True, 'delete': True},
                    'blog': {'create': True, 'read': True, 'update': True, 'delete': True},
                    'users': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'partners': {'create': True, 'read': True, 'update': True, 'delete': False},
                    'referrals': {'create': True, 'read': True, 'update': True, 'delete': True},
                    'statistics': {'create': False, 'read': True, 'update': False, 'delete': False}
                }
            },
            'admin_limited': {
                'display_name': 'Admin - Limited',
                'description': 'Can edit but not delete products and blog',
                'permissions': {
                    'products': {'create': True, 'read': True, 'update': True, 'delete': False},
                    'blog': {'create': True, 'read': True, 'update': True, 'delete': False},
                    'users': {'create': False, 'read': False, 'update': False, 'delete': False},
                    'partners': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'referrals': {'create': True, 'read': True, 'update': False, 'delete': False},
                    'statistics': {'create': False, 'read': True, 'update': False, 'delete': False}
                }
            }
        }
        return templates.get(template_name)


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
    
    author = db.relationship('User', backref='blog_posts')


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

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_name = db.Column(db.String(100))
    action = db.Column(db.String(50), nullable=False)  # create, update, delete, login, logout, approve, suspend, regenerate
    resource_type = db.Column(db.String(50), nullable=False)  # product, blog, user, partner, referral
    resource_id = db.Column(db.Integer)
    description = db.Column(db.String(500))
    details = db.Column(db.Text)  # JSON string of changes
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='activities')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'description': self.description,
            'details': json.loads(self.details) if self.details else None,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }