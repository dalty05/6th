from flask import Blueprint, request, jsonify, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, OTP, PasswordResetToken, EmailVerificationToken, LoginAttempt, Role, ActivityLog
from email_service import EmailService
from datetime import datetime, timedelta
import re
from functools import wraps
from services.activity_logger import log_activity

auth_bp = Blueprint('auth', __name__)
email_service = EmailService()



login_attempts_cache = {}

def rate_limit_check(email, ip, max_attempts=5, window_minutes=15):
    """Check rate limiting for login attempts"""
    key = f"{email}:{ip}"
    now = datetime.utcnow()
    
    if key not in login_attempts_cache:
        login_attempts_cache[key] = []
    
    # Clean old attempts
    login_attempts_cache[key] = [t for t in login_attempts_cache[key] 
                                  if now - t < timedelta(minutes=window_minutes)]
    
    if len(login_attempts_cache[key]) >= max_attempts:
        return False
    
    return True

def record_login_attempt(email, ip, success, user_id=None):
    """Record login attempt in database"""
    attempt = LoginAttempt(
        email=email,
        ip_address=ip,
        success=success,
        user_id=user_id
    )
    db.session.add(attempt)
    db.session.commit()
    
    # Update cache
    key = f"{email}:{ip}"
    if key not in login_attempts_cache:
        login_attempts_cache[key] = []
    login_attempts_cache[key].append(datetime.utcnow())

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def role_required(*roles):
    """Decorator for role-based access control"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            if current_user.role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ============================================================
# PUBLIC ROUTES
# ============================================================


@auth_bp.route('/auth/check-session', methods=['GET'])
def check_session():
    """Check if user has active session"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': current_user.to_dict()
        }), 200
    return jsonify({
        'authenticated': False
    }), 401




@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new admin account"""
    data = request.json
    email = data.get('email', '').lower().strip()
    full_name = data.get('full_name', '').strip()
    password = data.get('password')
    
    # Validate input
    if not all([email, full_name, password]):
        return jsonify({'error': 'All fields are required'}), 400
    
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Check if user exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 400
    
    # Validate password strength
    valid, message = validate_password(password)
    if not valid:
        return jsonify({'error': message}), 400
    
    # Check if this is the first user (becomes super admin)
    is_first_user = User.query.count() == 0
    role = 'super_admin' if is_first_user else 'admin'
    is_approved = is_first_user  # Super admin auto-approved
    
    # Create user
    user = User(
        email=email,
        full_name=full_name,
        role=role,
        is_approved=is_approved,
        is_active=True
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    # Create email verification token
    token_obj = EmailVerificationToken(
        user_id=user.id,
        token=EmailVerificationToken.generate_token(),
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.session.add(token_obj)
    db.session.commit()
    
    # Send verification email
    frontend_url = current_app.config.get('FRONTEND_URL', 'localhost:5173')
    if not email_service.send_verification_email(user, token_obj.token, frontend_url):
        
        return jsonify({'error': 'Registration succeeded, but verification email could not be sent. Please check SMTP settings.'}), 500
    
    return jsonify({
        'message': 'Registration successful. Please verify your email.',
        'role': role,
        'requires_approval': not is_first_user
    }), 201

@auth_bp.route('/auth/verify-email', methods=['POST'])
def verify_email():
    """Verify email with token"""
    data = request.json
    token = data.get('token')
    
    token_obj = EmailVerificationToken.query.filter_by(token=token, used=False).first()
    
    if not token_obj or not token_obj.is_valid():
        return jsonify({'error': 'Invalid or expired token'}), 400
    
    # Mark token as used and set user email as verified
    token_obj.used = True
    user = token_obj.user
    user.email_verified = True
    db.session.commit()
    
    # Notify super admins about new registration
    super_admins = User.query.filter_by(role='super_admin', is_active=True).all()
    frontend_url = current_app.config.get('FRONTEND_URL', 'https://propeller-outclass-parsnip.ngrok-free.dev')
    
    for super_admin in super_admins:
        email_service.send_approval_email(user, frontend_url)
    
    return jsonify({'message': 'Email verified successfully. Waiting for admin approval.'}), 200

@auth_bp.route('/auth/login/step1', methods=['POST'])
def login_step1():
    """Step 1: Verify email and password"""
    data = request.json
    email = data.get('email', '').lower().strip()
    password = data.get('password')
    ip_address = request.remote_addr
    
    # Rate limiting check
    if not rate_limit_check(email, ip_address):
        return jsonify({'error': 'Too many login attempts. Try again later.'}), 429
    
    # Find user
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        record_login_attempt(email, ip_address, False)
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check account status
    if not user.is_active:
        return jsonify({'error': 'Account is suspended. Contact administrator.'}), 401
    
    if not user.is_approved:
        return jsonify({'error': 'Account pending approval. You will be notified when approved.'}), 401
    
    if not user.email_verified:
        return jsonify({'error': 'Please verify your email first.'}), 401
    
    # Generate and send OTP
    otp_code = OTP.generate_otp()
    otp = OTP(
        user_id=user.id,
        otp_code=otp_code,
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    db.session.add(otp)
    db.session.commit()
    
    # Send OTP email
    try:
        from email_service import EmailService
        email_service = EmailService()
        email_service.send_otp_email(user, otp_code)
        print(f"✅ OTP email sent to {email}")
    except Exception as e:
        print(f"❌ Failed to send OTP email: {e}")

    print(f"\n{'='*50}")
    print(f"🔐 OTP LOGIN CODE FOR {email}")
    print(f"📱 CODE: {otp_code}")
    print(f"⏰ Valid for 10 minutes")
    print(f"{'='*50}\n")
    
    # Store email in session for step 2
    session['login_email'] = email
    
    return jsonify({
        'message': 'OTP sent to your email',
        'requires_otp': True
    }), 200

@auth_bp.route('/auth/login/step2', methods=['POST'])
def login_step2():
    """Step 2: Verify OTP and complete login"""
    data = request.json
    otp_code = data.get('otp_code')
    ip_address = request.remote_addr
    remember = data.get('remember', False)
    
    email = session.get('login_email')
    
    if not email:
        return jsonify({'error': 'Login session expired. Please start over.'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Verify OTP
    otp = OTP.query.filter_by(
        user_id=user.id,
        otp_code=otp_code,
        is_verified=False
    ).order_by(OTP.created_at.desc()).first()
    
    if not otp or not otp.is_valid():
        record_login_attempt(email, ip_address, False, user.id)
        return jsonify({'error': 'Invalid or expired OTP'}), 401
    
    # Mark OTP as verified
    otp.is_verified = True
    user.last_login = datetime.utcnow()
    user.last_login_ip = ip_address
    db.session.commit()
    
    # Login user
    login_user(user, remember=remember)
    
    # Clear login session
    session.pop('login_email', None)
    
    record_login_attempt(email, ip_address, True, user.id)
    
    #  Return user with tour flags
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'is_active': user.is_active,
            'is_approved': user.is_approved,
            'is_tour_manager': user.is_tour_manager,
            'is_tour_assistant': user.is_tour_assistant,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        },
        'is_super_admin': user.is_super_admin()
    }), 200

@auth_bp.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    data = request.json
    email = data.get('email', '').lower().strip()
    
    user = User.query.filter_by(email=email).first()
    
    # Don't reveal if user exists for security
    if user and user.is_active:
        token_obj = PasswordResetToken(
            user_id=user.id,
            token=PasswordResetToken.generate_token(),
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        db.session.add(token_obj)
        db.session.commit()
        
        frontend_url = current_app.config.get('FRONTEND_URL', 'https://propeller-outclass-parsnip.ngrok-free.dev')
        email_service.send_password_reset_email(user, token_obj.token, frontend_url)
    
    return jsonify({'message': 'If an account exists, you will receive a password reset email.'}), 200

@auth_bp.route('/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    data = request.json
    token = data.get('token')
    new_password = data.get('new_password')
    
    token_obj = PasswordResetToken.query.filter_by(token=token, used=False).first()
    
    if not token_obj or not token_obj.is_valid():
        return jsonify({'error': 'Invalid or expired token'}), 400
    
    # Validate new password
    valid, message = validate_password(new_password)
    if not valid:
        return jsonify({'error': message}), 400
    
    # Update password
    user = token_obj.user
    user.set_password(new_password)
    token_obj.used = True
    db.session.commit()
    
    return jsonify({'message': 'Password reset successful. You can now login.'}), 200

@auth_bp.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    """Logout user"""
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

# ============================================================
# SUPER ADMIN ONLY ROUTES
# ============================================================

@auth_bp.route('/admin/users', methods=['GET'])
@login_required
@role_required('super_admin')
def get_users():
    """Get all users (super admin only)"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@auth_bp.route('/admin/users', methods=['POST'])
@login_required
@role_required('super_admin')
def create_user():
    """Create a new user (super admin only)"""
    data = request.json
    email = data.get('email', '').lower().strip()
    full_name = data.get('full_name', '').strip()
    password = data.get('password')
    role = data.get('role', 'partner')
    is_active = data.get('is_active', True)
    is_approved = data.get('is_approved', True)
    
    # Validate input
    if not all([email, full_name, password]):
        return jsonify({'error': 'All fields are required'}), 400
    
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Check if user exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 400
    
    # Validate password strength
    valid, message = validate_password(password)
    if not valid:
        return jsonify({'error': message}), 400
    
    # Determine role by ID or name
    role_id = data.get('role_id')
    selected_role = None
    if role_id is not None:
        selected_role = Role.query.get(role_id)
        if not selected_role:
            return jsonify({'error': 'Role not found'}), 404
        role = selected_role.name
    else:
        role = data.get('role', 'partner')
        if role:
            selected_role = Role.query.filter_by(name=role).first()
            role_id = selected_role.id if selected_role else None

    # Determine tour role flags
    is_tour_manager = role == 'tour_manager'
    is_tour_assistant = role == 'tour_assistant'
    
    # Create user
    user = User(
        email=email,
        full_name=full_name,
        role=role,
        role_id=role_id,
        is_active=is_active,
        is_approved=is_approved,
        is_tour_manager=is_tour_manager,
        is_tour_assistant=is_tour_assistant,
        email_verified=True  # Auto-verified for admin-created users
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'User created successfully',
        'user': user.to_dict(),
        'temporary_password': password  # Only shown once
    }), 201

@auth_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@login_required
@role_required('super_admin')
def update_user(user_id):
    """Update user (super admin only)"""
    user = User.query.get_or_404(user_id)
    data = request.json
    
    if data.get('full_name'):
        user.full_name = data['full_name']
    
    if 'role_id' in data:
        if data['role_id'] is not None:
            selected_role = Role.query.get(data['role_id'])
            if not selected_role:
                return jsonify({'error': 'Role not found'}), 404
            user.role_id = selected_role.id
            user.role = selected_role.name
        else:
            user.role_id = None
            user.role = None
            user.is_active = False
    elif data.get('role'):
        requested_role = data['role']
        selected_role = Role.query.filter_by(name=requested_role).first()
        user.role = requested_role
        user.role_id = selected_role.id if selected_role else None

    if 'is_active' in data:
        user.is_active = data['is_active']
    
    if 'is_approved' in data:
        user.is_approved = data['is_approved']
    
    # Update tour flags based on role
    user.is_tour_manager = user.role == 'tour_manager'
    user.is_tour_assistant = user.role == 'tour_assistant'
    
    # Allow manual override of tour flags if needed
    if 'is_tour_manager' in data:
        user.is_tour_manager = data['is_tour_manager']
    
    if 'is_tour_assistant' in data:
        user.is_tour_assistant = data['is_tour_assistant']
    
    db.session.commit()
    
    return jsonify({
        'message': 'User updated successfully',
        'user': user.to_dict()
    }), 200

@auth_bp.route('/admin/users/<int:user_id>/approve', methods=['PUT'])
@login_required
@role_required('super_admin')
def approve_user(user_id):
    """Approve a user (super admin only)"""
    user = User.query.get_or_404(user_id)
    
    if user.is_approved:
        return jsonify({'error': 'User already approved'}), 400
    
    user.is_approved = True
    user.approved_by_id = current_user.id
    user.approved_at = datetime.utcnow()
    db.session.commit()
    
    # Send approval email
    frontend_url = current_app.config.get('FRONTEND_URL', 'https://propeller-outclass-parsnip.ngrok-free.dev')
    email_service.send_approval_email(user, frontend_url)
    
    return jsonify({'message': f'{user.full_name} has been approved'}), 200

@auth_bp.route('/admin/users/<int:user_id>/suspend', methods=['PUT'])
@login_required
@role_required('super_admin')
def suspend_user(user_id):
    """Suspend or activate a user (super admin only)"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot suspend yourself'}), 400
    
    data = request.json
    is_active = data.get('is_active', False)
    reason = data.get('reason', '')
    
    user.is_active = is_active
    db.session.commit()
    
    if not is_active:
        email_service.send_suspension_email(user, current_user, reason)
    
    status = 'suspended' if not is_active else 'activated'
    return jsonify({'message': f'User {status} successfully'}), 200

@auth_bp.route('/admin/users/<int:user_id>/activate', methods=['POST'])
@login_required
@role_required('super_admin')
def activate_user(user_id):
    """Activate a suspended user (super admin only)"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot activate yourself'}), 400
    
    user.is_active = True
    db.session.commit()
    
    return jsonify({'message': f'User {user.full_name} activated successfully'}), 200

@auth_bp.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@role_required('super_admin')
def reset_user_password(user_id):
    """Reset user password (super admin only)"""
    user = User.query.get_or_404(user_id)
    
    # Generate random password
    import random
    import string
    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({
        'message': 'Password reset successfully',
        'new_password': new_password
    }), 200

@auth_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@login_required
@role_required('super_admin')
def delete_user(user_id):
    """Delete a user (super admin only)"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200

# ============================================================
# SELF-SERVICE ROUTES
# ============================================================

@auth_bp.route('/admin/profile', methods=['GET'])
@login_required
def get_profile():
    """Get current user profile"""
    return jsonify(current_user.to_dict()), 200

@auth_bp.route('/admin/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update current user profile"""
    data = request.json
    full_name = data.get('full_name')
    
    if full_name:
        current_user.full_name = full_name
    
    db.session.commit()
    return jsonify({'message': 'Profile updated', 'user': current_user.to_dict()}), 200

@auth_bp.route('/admin/change-password', methods=['PUT'])
@login_required
def change_password():
    """Change current user password"""
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    valid, message = validate_password(new_password)
    if not valid:
        return jsonify({'error': message}), 400
    
    current_user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200

@auth_bp.route('/admin/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if current_user.is_authenticated:
        return jsonify({
            'is_admin': True,
            'user': current_user.to_dict(),
            'is_super_admin': current_user.is_super_admin()
        }), 200
    return jsonify({'is_admin': False}), 200

@auth_bp.route('/admin/check', methods=['GET'])
def check_auth_alias():
    """Alias for legacy admin auth checks"""
    return check_auth()



# Activity Log Endpoint c

@auth_bp.route('/admin/activities', methods=['GET'])
@login_required
def get_activities():
    """Get user's recent activities"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        activities = ActivityLog.query.filter_by(
            user_id=current_user.id
        ).order_by(
            ActivityLog.created_at.desc()
        ).limit(limit).all()
        
        return jsonify({
            'activities': [a.to_dict() for a in activities]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500