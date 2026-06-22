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

    def to_dict(self, include_permissions=False):
        """Convert user object to dictionary for API responses"""
        data = {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'is_approved': self.is_approved,
            'email_verified': self.email_verified,
            'referral_code': self.referral_code,
            'total_clicks': self.total_clicks,
            'total_conversions': self.total_conversions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'last_login_ip': self.last_login_ip,
            'permissions': None
        }

        if include_permissions:
            data['permissions'] = self.get_permissions()

        return data

    # ========== PERMISSION METHODS - MUST BE INSIDE THE CLASS ==========
    
    def get_permissions(self):
        """Get permissions for this user"""
        try:
            from permission_service import has_permission
        except ImportError:
            # Fallback if permission_service not available
            return {
                'products': {'read': True},
                'blog': {'read': True},
                'jobs': {'read': True},
                'outlets': {'read': True},
                'users': {'read': True if self.role == 'super_admin' else False},
                'partners': {'read': True if self.role == 'super_admin' else False},
                'referrals': {'read': True, 'create': True, 'update': True},
                'statistics': {'read': True},
                'contacts': {'read': True if self.role == 'super_admin' else False}
            }
        
        # Super admin has all permissions
        if self.role == 'super_admin':
            return {
                'products': {'create': True, 'read': True, 'update': True, 'delete': True},
                'blog': {'create': True, 'read': True, 'update': True, 'delete': True},
                'jobs': {'create': True, 'read': True, 'update': True, 'delete': True},
                'outlets': {'create': True, 'read': True, 'update': True, 'delete': True},
                'users': {'create': True, 'read': True, 'update': True, 'delete': True},
                'partners': {'create': True, 'read': True, 'update': True, 'delete': True},
                'referrals': {'create': True, 'read': True, 'update': True, 'delete': True},
                'statistics': {'create': True, 'read': True, 'update': True, 'delete': True},
                
                'contacts': {'create': True, 'read': True, 'update': True, 'delete': True}
            }
        
        resources = ['products', 'blog', 'jobs', 'outlets', 'users', 'partners', 'referrals', 'statistics',  'contacts']
        actions = ['create', 'read', 'update', 'delete']
        
        permissions = {}
        for resource in resources:
            permissions[resource] = {}
            for action in actions:
                permissions[resource][action] = has_permission(self, resource, action)
        
        return permissions

    def has_permission(self, resource, action):
        """Check if user has specific permission"""
        # Super admin bypass
        if self.role == 'super_admin':
            return True
        
        # First check UserPermission table (most specific)
        from models import UserPermission
        custom_perm = UserPermission.query.filter_by(
            user_id=self.id, 
            resource=resource, 
            action=action
        ).first()
        if custom_perm:
            return custom_perm.is_allowed
        
        # Then check JSON permissions field
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





def has_permission(self, resource, action):
    """Check if user has specific permission"""
    # Super admin bypass
    if self.role == 'super_admin':
        return True
    
    # First check UserPermission table (most specific)
    from models import UserPermission
    custom_perm = UserPermission.query.filter_by(
        user_id=self.id, 
        resource=resource, 
        action=action
    ).first()
    if custom_perm:
        return custom_perm.is_allowed
    
    # Then check JSON permissions field
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
    user = db.relationship('User', backref=db.backref('referral_links', lazy='dynamic',cascade='all, delete-orphan'))
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
    
    user = db.relationship('User', backref=db.backref('activities', cascade='all, delete-orphan'))
    
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
    

   


   #newsletter settings
class NewsletterSubscriber(db.Model):
    __tablename__ = 'newsletter_subscribers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    last_sent = db.Column(db.DateTime)



class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='unread')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'subject': self.subject,
            'message': self.message,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        


# job applications

class JobCategory(db.Model):
    __tablename__ = 'job_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    jobs = db.relationship('Job', backref='category', lazy=True)

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('job_categories.id'))
    location = db.Column(db.String(200))
    type = db.Column(db.String(50))  # Full-time, Part-time, Remote, Contract, Internship
    experience_level = db.Column(db.String(50))  # Entry, Intermediate, Senior, Expert
    salary_range = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    responsibilities = db.Column(db.Text)
    benefits = db.Column(db.Text)
    application_deadline = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    views_count = db.Column(db.Integer, default=0)
    applications_count = db.Column(db.Integer, default=0)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    created_by_user = db.relationship('User', backref='jobs_created')
    applications = db.relationship('JobApplication', backref='job', lazy=True, cascade='all, delete-orphan')

class JobApplication(db.Model):
    __tablename__ = 'job_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    
    # Applicant information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    cover_letter = db.Column(db.Text, nullable=False)
    cv_url = db.Column(db.String(500), nullable=False)
    portfolio_url = db.Column(db.String(500))
    linkedin_url = db.Column(db.String(500))
    
    # Status tracking
    status = db.Column(db.String(50), default='pending')  # pending, reviewed, shortlisted, rejected, hired
    admin_notes = db.Column(db.Text)
    rating = db.Column(db.Integer)  # 1-5 star rating from admin
    
    # Communication
    admin_reply = db.Column(db.Text)
    replied_at = db.Column(db.DateTime)
    replied_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Metadata
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    replied_by_user = db.relationship('User', backref='job_replies')
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"



class Outlet(db.Model):
    __tablename__ = 'outlets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # office_branch, depot, outlet
    description = db.Column(db.Text)
    address = db.Column(db.String(500), nullable=False)
    city = db.Column(db.String(100))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    working_hours = db.Column(db.String(500))
    services = db.Column(db.Text)  # JSON string of services
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_services_list(self):
        if self.services:
            import json
            return json.loads(self.services)
        return []
    
    def set_services_list(self, services_list):
        import json
        self.services = json.dumps(services_list)






class UserPermission(db.Model):
    """User-specific permissions - overrides role defaults"""
    __tablename__ = 'user_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource = db.Column(db.String(50), nullable=False)  # products, jobs, outlets, blog, referrals, users, contacts
    action = db.Column(db.String(20), nullable=False)    # create, read, update, delete
    is_allowed = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    user = db.relationship('User', foreign_keys=[user_id], backref='custom_permissions')
    creator = db.relationship('User', foreign_keys=[created_by])
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'resource', 'action', name='unique_user_permission'),
    )

class ResourcePermission(db.Model):
    """Resource-level permissions - control access to specific items"""
    __tablename__ = 'resource_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)  # product, job, outlet, blog_post
    resource_id = db.Column(db.Integer, nullable=False)       # specific item ID
    action = db.Column(db.String(20), nullable=False)         # read, update, delete
    is_allowed = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    user = db.relationship('User', foreign_keys=[user_id], backref='resource_permissions')
    creator = db.relationship('User', foreign_keys=[created_by])
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'resource_type', 'resource_id', 'action', name='unique_resource_permission'),
    )




class ReferralNavigation(db.Model):
    __tablename__ = 'referral_navigations'
    
    id = db.Column(db.Integer, primary_key=True)
    referral_code = db.Column(db.String(50), index=True, nullable=False)
    session_id = db.Column(db.String(100), index=True)
    
    # Action details
    action = db.Column(db.String(20), default='nav_click')  # nav_click, exit, page_view
    link_text = db.Column(db.String(200))
    link_href = db.Column(db.String(500))
    link_id = db.Column(db.String(100))
    link_class = db.Column(db.String(200))
    
    # Page context
    page_url = db.Column(db.String(500))
    page_title = db.Column(db.String(200))
    referrer_url = db.Column(db.String(500))
    
    # User context
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    screen_size = db.Column(db.String(50))
    
    # Time metrics
    time_spent = db.Column(db.Integer)  # seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'referral_code': self.referral_code,
            'action': self.action,
            'link_text': self.link_text,
            'link_href': self.link_href,
            'page_url': self.page_url,
            'page_title': self.page_title,
            'time_spent': self.time_spent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }