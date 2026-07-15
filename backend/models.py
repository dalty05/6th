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
    role = db.Column(db.String(20), default='partner')
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Partner specific fields
    referral_code = db.Column(db.String(50), unique=True)
    total_clicks = db.Column(db.Integer, default=0)
    total_conversions = db.Column(db.Integer, default=0)
    
    #  Tour management fields
    is_tour_manager = db.Column(db.Boolean, default=False)
    is_tour_assistant = db.Column(db.Boolean, default=False)
    
    # Permission JSON field
    permissions = db.Column(db.Text, default='{}')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(50))

    
        # Role relationship 
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    
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
    
    # ✅ RENAMED METHODS (no longer conflict with columns)
    def has_tour_manager_role(self):
        return self.role == 'tour_manager' or self.is_tour_manager
    
    def has_tour_assistant_role(self):
        return self.role == 'tour_assistant' or self.is_tour_assistant
    
    def is_tour_staff(self):
        return self.has_tour_manager_role() or self.has_tour_assistant_role()
    
    def to_dict(self, include_permissions=False):
        """Convert user object to dictionary for API responses"""
        data = {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'role_id': self.role_id,
            'is_active': self.is_active,
            'is_approved': self.is_approved,
            'email_verified': self.email_verified,
            'referral_code': self.referral_code,
            'total_clicks': self.total_clicks,
            'total_conversions': self.total_conversions,
            'is_tour_manager': self.is_tour_manager, 
            'is_tour_assistant': self.is_tour_assistant,  
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'last_login_ip': self.last_login_ip,
            'permissions': None
        }

        if include_permissions:
            data['permissions'] = self.get_permissions()

        return data

    # ... rest of your User methods ...


# ============================================================
# TOUR MODELS
# ============================================================



class TourPackage(db.Model):
    """Main tour packages with manager-configurable settings"""
    __tablename__ = 'tour_packages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    short_description = db.Column(db.String(200))
    
    # Pricing
    base_price = db.Column(db.Float, nullable=False)
    min_people = db.Column(db.Integer, default=1)
    max_people = db.Column(db.Integer, default=300)
    commitment_percentage = db.Column(db.Float, default=30.0)
    discount_tiers = db.Column(db.JSON, default={
        '1-50': 0.05,
        '51-100': 0.10,
        '101-150': 0.15,
        '151-200': 0.20,
        '201+': 0.25
    })
    
    
    
    # Tour details
    duration_hours = db.Column(db.Integer, default=2)
    includes = db.Column(db.JSON, default=[])
    excludes = db.Column(db.JSON, default=[])
    
    # Media
    image_url = db.Column(db.String(255))
    gallery_images = db.Column(db.JSON)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    bookings = db.relationship('TourBooking', back_populates='package', lazy='dynamic')
    availability = db.relationship('TourAvailability', back_populates='package', lazy='dynamic')
    
    def get_price_for_people(self, people_count):
        """Calculate price based on number of people"""
        discount = 0
        
        for tier, discount_rate in self.discount_tiers.items():
            if '-' in tier:
                min_p, max_p = map(int, tier.split('-'))
                if min_p <= people_count <= max_p:
                    discount = discount_rate
                    break
            elif tier.endswith('+'):
                min_p = int(tier[:-1])
                if people_count >= min_p:
                    discount = discount_rate
                    break
        
        subtotal = self.base_price * people_count
        discount_amount = subtotal * discount
        total = subtotal - discount_amount
        
        return {
            'base_price': self.base_price,
            'people_count': people_count,
            'subtotal': subtotal,
            'discount_percentage': discount * 100,
            'discount_amount': discount_amount,
            'total': total,
            'tier_applied': self._get_tier_label(people_count)
        }
    
    def _get_tier_label(self, people_count):
        for tier, discount_rate in self.discount_tiers.items():
            if '-' in tier:
                min_p, max_p = map(int, tier.split('-'))
                if min_p <= people_count <= max_p:
                    return f'{tier} ({discount_rate * 100}%)'
            elif tier.endswith('+'):
                min_p = int(tier[:-1])
                if people_count >= min_p:
                    return f'{tier} ({discount_rate * 100}%)'
        return 'No discount'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'short_description': self.short_description,
            'base_price': self.base_price,
            'min_people': self.min_people,
            'max_people': self.max_people,
            'commitment_percentage': self.commitment_percentage,
            'discount_tiers': self.discount_tiers,
            'duration_hours': self.duration_hours,
            'includes': self.includes,
            'excludes': self.excludes,
            'image_url': self.image_url,
            'gallery_images': self.gallery_images,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class TourBooking(db.Model):
    """Complete booking lifecycle"""
    __tablename__ = 'tour_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Booking details
    package_id = db.Column(db.Integer, db.ForeignKey('tour_packages.id'), nullable=False)
    tour_date = db.Column(db.DateTime, nullable=False)
    people_count = db.Column(db.Integer, nullable=False)
    
    # Customer details
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False, index=True)
    customer_phone = db.Column(db.String(20), nullable=False)
    
    # Optional details
    special_requirements = db.Column(db.Text)
    preferred_language = db.Column(db.String(20), default='English')
    group_name = db.Column(db.String(100))
    
    # Pricing
    price_per_person = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    discount_applied = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, nullable=False)
    
    # Payment tracking
    payment_status = db.Column(db.String(20), default='pending')
    commitment_amount = db.Column(db.Float, default=0)
    commitment_paid = db.Column(db.Boolean, default=False)
    commitment_paid_date = db.Column(db.DateTime)
    full_payment_date = db.Column(db.DateTime)
    payment_notes = db.Column(db.Text)
    
    # Booking status
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, commitment_pending, cleared, completed, cancelled, rejected
    
    # Change requests
    change_requested_date = db.Column(db.DateTime)
    change_request_new_date = db.Column(db.DateTime)
    change_request_reason = db.Column(db.Text)
    change_request_status = db.Column(db.String(20))  # pending, approved, rejected
    
    # Audit
    notes = db.Column(db.Text)
    cancellation_reason = db.Column(db.Text)
    cancellation_date = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    customer_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    package = db.relationship('TourPackage', back_populates='bookings')
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    customer_user = db.relationship('User', foreign_keys=[customer_user_id])
    payments = db.relationship('TourPayment', back_populates='booking', lazy='dynamic')
    invoice = db.relationship('TourInvoice', back_populates='booking', uselist=False)
    
    def generate_reference(self):
        import random
        import string
        year = datetime.utcnow().year
        random_digits = ''.join(random.choices(string.digits, k=5))
        self.reference = f"TU-{year}-{random_digits}"
        return self.reference
    
    def calculate_price(self):
        if self.package:
            price_data = self.package.get_price_for_people(self.people_count)
            self.price_per_person = price_data['base_price']
            self.subtotal = price_data['subtotal']
            self.discount_applied = price_data['discount_amount']
            self.total_amount = price_data['total']
            return price_data
        return None
    
    def can_edit(self):
        return self.status in ['pending', 'confirmed', 'commitment_pending']
    
    def can_cancel(self):
        return self.status not in ['completed', 'cancelled', 'rejected']
    
    def request_date_change(self, new_date, reason):
        self.change_requested_date = datetime.utcnow()
        self.change_request_new_date = new_date
        self.change_request_reason = reason
        self.change_request_status = 'pending'
        self.status = 'change_requested'
    
    def approve_date_change(self):
        if self.change_request_status == 'pending':
            self.tour_date = self.change_request_new_date
            self.change_request_status = 'approved'
            self.status = 'confirmed'
            return True
        return False
    
    def reject_date_change(self):
        if self.change_request_status == 'pending':
            self.change_request_status = 'rejected'
            self.status = 'confirmed'
            return True
        return False
    

    def to_dict(self, include_package=False):
        data = {
            'id': self.id,
            'reference': self.reference,
            'tour_date': self.tour_date.isoformat() if self.tour_date else None,
            'people_count': self.people_count,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'special_requirements': self.special_requirements,
            'group_name': self.group_name,
            'price_per_person': self.price_per_person,
            'subtotal': self.subtotal,
            'discount_applied': self.discount_applied,
            'total_amount': self.total_amount,
            'payment_status': self.payment_status,
            'commitment_amount': self.commitment_amount,
            'commitment_paid': self.commitment_paid,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_package and self.package:
            data['package'] = self.package.to_dict()
        
        return data



class TourAvailability(db.Model):
    """Tour availability - simplified (no capacity, only blocking)"""
    __tablename__ = 'tour_availability'
    
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('tour_packages.id'), nullable=False)
    
    date = db.Column(db.Date, nullable=False, index=True)
    


    is_blocked = db.Column(db.Boolean, default=False)
    block_reason = db.Column(db.String(200))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    package = db.relationship('TourPackage', back_populates='availability')
    
    @property
    def is_available(self):
        """Check if the date is available"""
        return not self.is_blocked
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'is_blocked': self.is_blocked,
            'block_reason': self.block_reason,
            'is_available': self.is_available
        }



class TourPayment(db.Model):
    """Payment tracking (manual for now)"""
    __tablename__ = 'tour_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('tour_bookings.id'), nullable=False)
    
    amount = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)  # commitment, balance, full
    payment_method = db.Column(db.String(20), default='manual')  # manual, mpesa, bank_transfer
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Manual payment tracking
    reference_number = db.Column(db.String(100))
    payment_proof_url = db.Column(db.String(255))
    verified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    verification_date = db.Column(db.DateTime)
    verification_notes = db.Column(db.Text)
    
    status = db.Column(db.String(20), default='pending')  # pending, verified, rejected
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    booking = db.relationship('TourBooking', back_populates='payments')
    verified_by = db.relationship('User', foreign_keys=[verified_by_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'payment_method': self.payment_method,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'reference_number': self.reference_number,
            'status': self.status,
            'verification_notes': self.verification_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TourInvoice(db.Model):
    """PDF certificate/invoice tracking"""
    __tablename__ = 'tour_invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('tour_bookings.id'), nullable=False)
    
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    pdf_url = db.Column(db.String(255))
    qr_code_url = db.Column(db.String(255))
    
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    download_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    booking = db.relationship('TourBooking', back_populates='invoice')
    
    def generate_invoice_number(self):
        import random
        import string
        year = datetime.utcnow().year
        random_digits = ''.join(random.choices(string.digits, k=6))
        self.invoice_number = f"INV-{year}-{random_digits}"
        return self.invoice_number
    
    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'invoice_number': self.invoice_number,
            'pdf_url': self.pdf_url,
            'qr_code_url': self.qr_code_url,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'download_count': self.download_count
        }


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
    user = db.relationship('User', backref=db.backref('referral_links', lazy='dynamic', cascade='all, delete-orphan'))
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
        
        recent_click = ReferralClick.query.filter(
            ReferralClick.link_id == self.id,
            ReferralClick.ip_address == ip_address,
            ReferralClick.clicked_at > datetime.utcnow() - timedelta(hours=24)
        ).first()
        
        if not recent_click:
            self.unique_clicks += 1
        
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
    permissions = db.Column(db.Text, nullable=False)
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
    is_active = db.Column(db.Boolean, default=True)
    
    # ✅ QR Code fields
    slug = db.Column(db.String(200), unique=True, nullable=True, index=True)
    qr_code_url = db.Column(db.String(500), nullable=True)
    qr_code_generated_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def generate_slug(self):
        """Generate a URL-friendly slug from product name"""
        import re
        slug = self.name.lower().strip()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        return slug
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'category': self.category,
            'description': self.description,
            'image_url': self.image_url,
            'benefits': self.benefits,
            'packaging_sizes': self.packaging_sizes,
            'nutritional_info': self.nutritional_info,
            'ingredients': self.ingredients,
            'featured': self.featured,
            'is_active': self.is_active,
            'qr_code_url': self.qr_code_url,
            'qr_code_generated_at': self.qr_code_generated_at.isoformat() if self.qr_code_generated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }




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
    action = db.Column(db.String(50), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.Integer)
    description = db.Column(db.String(500))
    details = db.Column(db.Text)
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


# ============================================================
# JOB MODELS
# ============================================================

class JobCategory(db.Model):
    """Job categories for organizing job listings"""
    __tablename__ = 'job_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jobs = db.relationship('Job', back_populates='category', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'icon': self.icon,
            'is_active': self.is_active,
            'job_count': self.jobs.count() if self.jobs else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<JobCategory {self.name}>'


class Job(db.Model):
    """Job listings with full details"""
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    
    category_id = db.Column(db.Integer, db.ForeignKey('job_categories.id'), nullable=True)
    
    location = db.Column(db.String(200))
    type = db.Column(db.String(50))
    experience_level = db.Column(db.String(50))
    salary_range = db.Column(db.String(100))
    
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    responsibilities = db.Column(db.Text)
    benefits = db.Column(db.Text)
    
    application_deadline = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    views_count = db.Column(db.Integer, default=0)
    applications_count = db.Column(db.Integer, default=0)
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = db.relationship('JobCategory', back_populates='jobs', foreign_keys=[category_id])
    created_by_user = db.relationship('User', backref='jobs_created', foreign_keys=[created_by])
    applications = db.relationship('JobApplication', back_populates='job', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_applications=False):
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'category_id': self.category_id,
            'category': self.category.name if self.category else None,
            'location': self.location,
            'type': self.type,
            'experience_level': self.experience_level,
            'salary_range': self.salary_range,
            'description': self.description,
            'requirements': self.requirements,
            'responsibilities': self.responsibilities,
            'benefits': self.benefits,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'views_count': self.views_count,
            'applications_count': self.applications_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_applications:
            data['applications'] = [app.to_dict() for app in self.applications]
        
        return data
    
    def increment_views(self):
        self.views_count += 1
        db.session.commit()
    
    def increment_applications(self):
        self.applications_count += 1
        db.session.commit()
    
    def __repr__(self):
        return f'<Job {self.title}>'


class JobApplication(db.Model):
    """Job applications from candidates"""
    __tablename__ = 'job_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    phone = db.Column(db.String(20))
    
    cover_letter = db.Column(db.Text, nullable=False)
    cv_url = db.Column(db.String(500), nullable=False)
    portfolio_url = db.Column(db.String(500))
    linkedin_url = db.Column(db.String(500))
    
    status = db.Column(db.String(50), default='pending')
    admin_notes = db.Column(db.Text)
    rating = db.Column(db.Integer)
    
    admin_reply = db.Column(db.Text)
    replied_at = db.Column(db.DateTime)
    replied_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = db.relationship('Job', back_populates='applications', foreign_keys=[job_id])
    replied_by_user = db.relationship('User', backref='job_replies', foreign_keys=[replied_by])
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'job_title': self.job.title if self.job else None,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'email': self.email,
            'phone': self.phone,
            'cover_letter': self.cover_letter,
            'cv_url': self.cv_url,
            'portfolio_url': self.portfolio_url,
            'linkedin_url': self.linkedin_url,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'rating': self.rating,
            'admin_reply': self.admin_reply,
            'replied_at': self.replied_at.isoformat() if self.replied_at else None,
            'replied_by': self.replied_by,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<JobApplication {self.get_full_name()} for job {self.job_id}>'




class Outlet(db.Model):
    __tablename__ = 'outlets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.String(500), nullable=False)
    city = db.Column(db.String(100))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    working_hours = db.Column(db.String(500))
    services = db.Column(db.Text)
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
    __tablename__ = 'user_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(20), nullable=False)
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
    __tablename__ = 'resource_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(20), nullable=False)
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
    
    action = db.Column(db.String(20), default='nav_click')
    link_text = db.Column(db.String(200))
    link_href = db.Column(db.String(500))
    link_id = db.Column(db.String(100))
    link_class = db.Column(db.String(200))
    
    page_url = db.Column(db.String(500))
    page_title = db.Column(db.String(200))
    referrer_url = db.Column(db.String(500))
    
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    screen_size = db.Column(db.String(50))
    
    time_spent = db.Column(db.Integer)
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
    
# ============ DYNAMIC ROLE MODELS ============

class Role(db.Model):
    """Dynamic roles that can be created by super admin"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(200))
    is_system = db.Column(db.Boolean, default=False)  # Can't delete system roles
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    users = db.relationship('User', backref='role_ref', foreign_keys='User.role_id')
    components = db.relationship('RoleComponent', back_populates='role', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_system': self.is_system,
            'is_active': self.is_active,
            'component_count': len(self.components),
            'user_count': len(self.users),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'components': [rc.component.to_dict() for rc in self.components]
        }
    
    def __repr__(self):
        return f'<Role {self.name}>'


class DashboardComponent(db.Model):
    """Dashboard components that can be assigned to roles"""
    __tablename__ = 'dashboard_components'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False, index=True)  # 'products', 'tours', etc.
    label = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(50), default='fas fa-cube')  # FontAwesome class
    component_name = db.Column(db.String(100))  # Vue component name
    path = db.Column(db.String(100))  # URL path
    description = db.Column(db.String(200))
    section = db.Column(db.String(50), default='Main')  # Group in sidebar
    is_active = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)
    
    # Permissions mapping 
    required_permissions = db.Column(db.JSON, default=list)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = db.relationship('RoleComponent', back_populates='component', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'label': self.label,
            'icon': self.icon,
            'component_name': self.component_name,
            'path': self.path,
            'description': self.description,
            'section': self.section,
            'is_active': self.is_active,
            'order': self.order,
            'required_permissions': self.required_permissions or []
        }
    
    def __repr__(self):
        return f'<DashboardComponent {self.key}>'

#  RoleComponent

class RoleComponent(db.Model):
    """Mapping between roles and dashboard components with action overrides"""
    __tablename__ = 'role_components'
    
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    component_id = db.Column(db.Integer, db.ForeignKey('dashboard_components.id'), nullable=False)
    
    order = db.Column(db.Integer, default=0)  
    
    # ✅ Action overrides
    action_overrides = db.Column(db.JSON, default={})
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    role = db.relationship('Role', back_populates='components')
    component = db.relationship('DashboardComponent', back_populates='roles')
    
    __table_args__ = (
        db.UniqueConstraint('role_id', 'component_id', name='unique_role_component'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'role_id': self.role_id,
            'component_id': self.component_id,
            'component': self.component.to_dict() if self.component else None,
            'action_overrides': self.action_overrides or {},
            'order': self.order  
        }
