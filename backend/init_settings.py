# init_settings.py
from app import app, db
from models import SystemSetting

default_settings = [
    # General Settings
    {'key': 'site_name', 'value': 'Meru Dairy', 'group': 'general', 'description': 'Website name', 'is_public': True},
    {'key': 'site_logo', 'value': '/logo.png', 'group': 'general', 'description': 'Site logo URL', 'is_public': True},
    {'key': 'contact_email', 'value': 'oyigodalton@gmail.com', 'group': 'general', 'description': 'Default contact email', 'is_public': False},
    {'key': 'contact_phone', 'value': '+254 710 901 376', 'group': 'general', 'description': 'Contact phone number', 'is_public': True},
    {'key': 'company_address', 'value': 'P.O. Box 2919, Meru-Kenya', 'group': 'general', 'description': 'Company address', 'is_public': True},
    
    # Email Settings
    {'key': 'smtp_server', 'value': 'smtp.gmail.com', 'group': 'email', 'description': 'SMTP server address', 'is_public': False},
    {'key': 'smtp_port', 'value': '587', 'group': 'email', 'description': 'SMTP port', 'is_public': False},
    {'key': 'smtp_username', 'value': '', 'group': 'email', 'description': 'SMTP username', 'is_public': False},
    {'key': 'smtp_password', 'value': '', 'group': 'email', 'description': 'SMTP password', 'is_public': False},
    {'key': 'email_from_name', 'value': 'Meru Dairy', 'group': 'email', 'description': 'Sender name for emails', 'is_public': False},
    
    # Security Settings
    {'key': 'session_timeout', 'value': '60', 'group': 'security', 'description': 'Session timeout in minutes', 'is_public': False},
    {'key': 'max_login_attempts', 'value': '5', 'group': 'security', 'description': 'Maximum failed login attempts', 'is_public': False},
    {'key': 'password_min_length', 'value': '8', 'group': 'security', 'description': 'Minimum password length', 'is_public': False},
    {'key': 'otp_expiry_minutes', 'value': '10', 'group': 'security', 'description': 'OTP expiration in minutes', 'is_public': False},
    
    # Referral Settings
    {'key': 'referral_default_destination', 'value': 'https://merudairy.co.ke/products', 'group': 'referral', 'description': 'Default referral destination URL', 'is_public': False},
    {'key': 'referral_conversion_days', 'value': '30', 'group': 'referral', 'description': 'Days to track conversions', 'is_public': False},
    
    # Blog Settings
    {'key': 'blog_posts_per_page', 'value': '9', 'group': 'blog', 'description': 'Blog posts per page', 'is_public': True},
    {'key': 'blog_default_image', 'value': '/images/default-blog.jpg', 'group': 'blog', 'description': 'Default blog image URL', 'is_public': True},
    
    # Product Settings
    {'key': 'products_per_page', 'value': '12', 'group': 'product', 'description': 'Products per page', 'is_public': True},
    {'key': 'featured_products_count', 'value': '6', 'group': 'product', 'description': 'Number of featured products', 'is_public': True},
    
    # Job Settings
    {'key': 'jobs_per_page', 'value': '10', 'group': 'job', 'description': 'Jobs per page', 'is_public': True},
    {'key': 'application_deadline_days', 'value': '30', 'group': 'job', 'description': 'Default application deadline in days', 'is_public': False},
    
    # Outlet Settings
    {'key': 'outlets_per_page', 'value': '12', 'group': 'outlet', 'description': 'Outlets per page', 'is_public': True},
]

def init_settings():
    """Initialize default settings if they don't exist"""
    with app.app_context():
        for setting in default_settings:
            existing = SystemSetting.query.filter_by(key=setting['key']).first()
            if not existing:
                s = SystemSetting(**setting)
                db.session.add(s)
                print(f"Added setting: {setting['key']}")
        db.session.commit()
        print("Settings initialization complete!")

if __name__ == '__main__':
    init_settings()