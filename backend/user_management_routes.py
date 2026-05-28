# user_management_routes.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, User
from werkzeug.security import generate_password_hash
import re

user_mgmt_bp = Blueprint('user_mgmt', __name__)

def role_required(*roles):
    from functools import wraps
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

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

@user_mgmt_bp.route('/admin/users', methods=['GET'])
@login_required
@role_required('super_admin')
def get_users():
    """Get all users (super admin only)"""
    users = User.query.all()
    return jsonify([user.to_dict(include_permissions=True) for user in users]), 200

@user_mgmt_bp.route('/admin/users', methods=['POST'])
@login_required
@role_required('super_admin')
def create_user():
    """Create a new user (admin or partner)"""
    data = request.json
    email = data.get('email', '').lower().strip()
    full_name = data.get('full_name', '').strip()
    password = data.get('password')
    role = data.get('role', 'partner')
    
    # Validate input
    if not all([email, full_name, password]):
        return jsonify({'error': 'All fields are required'}), 400
    
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    valid, message = validate_password(password)
    if not valid:
        return jsonify({'error': message}), 400
    
    if role not in ['admin', 'partner']:
        return jsonify({'error': 'Invalid role. Must be admin or partner'}), 400
    
    # Check if user exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create user
    user = User(
        email=email,
        full_name=full_name,
        role=role,
        is_approved=True,  # Auto-approve since super admin creates
        is_active=True,
        created_by_id=current_user.id
    )
    user.set_password(password)
    
    # Generate referral code for partners
    if role == 'partner':
        user.generate_referral_code()
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': f'{role.capitalize()} created successfully',
        'user': user.to_dict()
    }), 201

@user_mgmt_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@login_required
@role_required('super_admin')
def update_user(user_id):
    """Update user details"""
    user = User.query.get_or_404(user_id)
    data = request.json
    
    if user.role == 'super_admin':
        return jsonify({'error': 'Cannot modify super admin'}), 403
    
    if 'full_name' in data:
        user.full_name = data['full_name']
    
    if 'role' in data and data['role'] in ['admin', 'partner']:
        old_role = user.role
        user.role = data['role']
        
        # Generate referral code if becoming a partner
        if data['role'] == 'partner' and not user.referral_code:
            user.generate_referral_code()
    
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({'message': 'User updated successfully', 'user': user.to_dict()}), 200

@user_mgmt_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@login_required
@role_required('super_admin')
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    
    if user.role == 'super_admin':
        return jsonify({'error': 'Cannot delete super admin'}), 403
    
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot delete yourself'}), 403
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200

@user_mgmt_bp.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@role_required('super_admin')
def reset_user_password(user_id):
    """Reset user password"""
    user = User.query.get_or_404(user_id)
    data = request.json
    new_password = data.get('new_password')
    
    if user.role == 'super_admin':
        return jsonify({'error': 'Cannot reset super admin password'}), 403
    
    valid, message = validate_password(new_password)
    if not valid:
        return jsonify({'error': message}), 400
    
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': 'Password reset successfully'}), 200

@user_mgmt_bp.route('/admin/users/<int:user_id>/regenerate-code', methods=['POST'])
@login_required
@role_required('super_admin')
def regenerate_referral_code(user_id):
    """Regenerate referral code for a partner"""
    user = User.query.get_or_404(user_id)
    
    if user.role != 'partner':
        return jsonify({'error': 'Only partners have referral codes'}), 400
    
    user.generate_referral_code()
    db.session.commit()
    
    return jsonify({'referral_code': user.referral_code}), 200