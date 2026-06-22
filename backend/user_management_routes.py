# backend/user_management_routes.py
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, User, UserPermission, ActivityLog
from email_service import email_service
from datetime import datetime
import json
import secrets
import string
from functools import wraps









user_mgmt_bp = Blueprint('user_mgmt', __name__)

def super_admin_required(f):
    """Decorator to restrict access to super admin only"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        if current_user.role != 'super_admin':
            return jsonify({'error': 'Super admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def log_activity(user_id, user_name, action, resource_type, resource_id, description, ip_address=None, user_agent=None):
    """Log user activity"""
    try:
        from flask import request
        log = ActivityLog(
            user_id=user_id,
            user_name=user_name,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            ip_address=ip_address or request.remote_addr,
            user_agent=user_agent or request.headers.get('User-Agent', '')
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")
        db.session.rollback()

# ========== GET ALL USERS ==========
@user_mgmt_bp.route('/admin/users', methods=['GET'])
@login_required
@super_admin_required
def get_users():
    """Get all users - Super Admin only"""
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify([{
            'id': u.id,
            'email': u.email,
            'full_name': u.full_name,
            'role': u.role,
            'is_active': u.is_active,
            'is_approved': u.is_approved,
            'email_verified': u.email_verified,
            'referral_code': u.referral_code,
            'total_clicks': u.total_clicks,
            'total_conversions': u.total_conversions,
            'created_at': u.created_at.isoformat() if u.created_at else None,
            'last_login': u.last_login.isoformat() if u.last_login else None
        } for u in users]), 200
    except Exception as e:
        print(f"Error in get_users: {e}")
        return jsonify([]), 200

# ========== GET SINGLE USER ==========
@user_mgmt_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@login_required
@super_admin_required
def get_user(user_id):
    """Get single user details - Super Admin only"""
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'is_active': user.is_active,
            'is_approved': user.is_approved,
            'email_verified': user.email_verified,
            'referral_code': user.referral_code,
            'total_clicks': user.total_clicks,
            'total_conversions': user.total_conversions,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }), 200
    except Exception as e:
        print(f"Error in get_user: {e}")
        return jsonify({'error': 'User not found'}), 404

# ========== CREATE USER ==========
@user_mgmt_bp.route('/admin/users', methods=['POST'])
@login_required
@super_admin_required
def create_user():
    """Create a new user - Super Admin only"""
    try:
        data = request.json
        email = data.get('email', '').lower().strip()
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'User with this email already exists'}), 400
        
        # Generate random password
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        
        user = User(
            email=email,
            full_name=data.get('full_name', '').strip(),
            role=data.get('role', 'partner'),
            is_active=data.get('is_active', True),
            is_approved=data.get('is_approved', True),
            email_verified=True,
            created_by_id=current_user.id
        )
        user.set_password(temp_password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate referral code for partner
        if user.role == 'partner':
            user.generate_referral_code()
            db.session.commit()
        
        # ========== SEND WELCOME EMAIL WITH PASSWORD ==========
        try:
            frontend_url = current_app.config.get('FRONTEND_URL', 'https://propeller-outclass-parsnip.ngrok-free.dev')
            email_sent = email_service.send_welcome_email(user, temp_password)
            if email_sent:
                print(f"✅ Welcome email sent to {user.email}")
            else:
                print(f"⚠️ Failed to send welcome email to {user.email}")
        except Exception as e:
            print(f"❌ Error sending welcome email: {e}")
        
        # Log activity
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='create',
            resource_type='user',
            resource_id=user.id,
            description=f'Created user: {user.email} with role {user.role}'
        )
        
        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'temporary_password': temp_password  # Only shown once
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in create_user: {e}")
        return jsonify({'error': str(e)}), 500

# ========== UPDATE USER ==========
@user_mgmt_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@login_required
@super_admin_required
def update_user(user_id):
    """Update a user - Super Admin only"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.json
        
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'role' in data:
            user.role = data['role']
            # Generate referral code if becoming partner
            if user.role == 'partner' and not user.referral_code:
                user.generate_referral_code()
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'is_approved' in data:
            user.is_approved = data['is_approved']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        # If user was approved via this update, send approval email
        if 'is_approved' in data and data['is_approved'] and not user.is_approved:
            try:
                frontend_url = current_app.config.get('FRONTEND_URL', 'https://propeller-outclass-parsnip.ngrok-free.dev')
                email_service.send_approval_email(user, frontend_url)
                print(f"✅ Approval email sent to {user.email}")
            except Exception as e:
                print(f"❌ Error sending approval email: {e}")
        
        # Log activity
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='update',
            resource_type='user',
            resource_id=user.id,
            description=f'Updated user: {user.email}'
        )
        
        return jsonify({'message': 'User updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_user: {e}")
        return jsonify({'error': str(e)}), 500

# ========== DELETE USER ==========

# ========== DELETE USER (Permanent) ==========
@user_mgmt_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@login_required
@super_admin_required
def delete_user(user_id):
    """Permanently delete a user and all associated data - Super Admin only"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent deleting yourself
        if user.id == current_user.id:
            return jsonify({'error': 'You cannot delete your own account'}), 400
        
        # Store user info for logging before deletion
        user_email = user.email
        user_name = user.full_name
        
        # Delete associated data first (foreign key relationships)
        # Delete referral links
        from models import ReferralLink, ReferralClick, UserPermission, ResourcePermission, ActivityLog, BlogPost, JobApplication
        
        # Delete referral clicks
        for link in user.referral_links:
            ReferralClick.query.filter_by(link_id=link.id).delete()
        
        # Delete referral links
        ReferralLink.query.filter_by(user_id=user.id).delete()
        
        # Delete user permissions
        UserPermission.query.filter_by(user_id=user.id).delete()
        ResourcePermission.query.filter_by(user_id=user.id).delete()
        
        # Delete activity logs
        ActivityLog.query.filter_by(user_id=user.id).delete()
        
        # Update blog posts (set author to NULL instead of deleting)
        BlogPost.query.filter_by(author_id=user.id).update({'author_id': None})
        
        # Update job applications (set replied_by to NULL)
        JobApplication.query.filter_by(replied_by=user.id).update({'replied_by': None})
        
        # Finally delete the user
        db.session.delete(user)
        db.session.commit()
        
        # Log activity (using current user info since user is deleted)
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='delete_permanent',
            resource_type='user',
            resource_id=user_id,
            description=f'Permanently deleted user: {user_email} ({user_name})'
        )
        
        return jsonify({'message': f'User {user_email} has been permanently deleted'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_user: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ========== APPROVE USER ==========
@user_mgmt_bp.route('/admin/users/<int:user_id>/approve', methods=['POST'])
@login_required
@super_admin_required
def approve_user(user_id):
    """Approve a user - Super Admin only"""
    try:
        user = User.query.get_or_404(user_id)
        
        if user.is_approved:
            return jsonify({'error': 'User already approved'}), 400
        
        user.is_approved = True
        db.session.commit()
        
        # ========== SEND APPROVAL EMAIL ==========
        try:
            frontend_url = current_app.config.get('FRONTEND_URL', 'https://propeller-outclass-parsnip.ngrok-free.dev')
            email_service.send_approval_email(user, frontend_url)
            print(f"✅ Approval email sent to {user.email}")
        except Exception as e:
            print(f"❌ Error sending approval email: {e}")
        
        # Log activity
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='approve',
            resource_type='user',
            resource_id=user.id,
            description=f'Approved user: {user.email}'
        )
        
        return jsonify({'message': 'User approved successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in approve_user: {e}")
        return jsonify({'error': str(e)}), 500

# ========== SUSPEND USER ==========

# ========== SUSPEND USER (with email) ==========
@user_mgmt_bp.route('/admin/users/<int:user_id>/suspend', methods=['POST'])
@login_required
@super_admin_required
def suspend_user(user_id):
    """Suspend a user - Super Admin only"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent suspending yourself
        if user.id == current_user.id:
            return jsonify({'error': 'You cannot suspend your own account'}), 400
        
        # Check if already suspended
        if not user.is_active:
            return jsonify({'error': 'User is already suspended'}), 400
        
        # Get reason from request
        data = request.json or {}
        reason = data.get('reason', 'No reason provided')
        
        # Suspend the user
        user.is_active = False
        db.session.commit()
        
        # ========== SEND SUSPENSION EMAIL ==========
        try:
            frontend_url = current_app.config.get('FRONTEND_URL', 'https://propeller-outclass-parsnip.ngrok-free.dev')
            login_url = f"{frontend_url}/admin/login"
            
            subject = f"Account Suspended - Meru Dairy Admin Portal"
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Account Suspended</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #dc2626; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ padding: 30px; background: #f9fafb; }}
                    .reason-box {{ background: white; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc2626; }}
                    .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #ddd; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Account Suspended</h2>
                    </div>
                    <div class="content">
                        <p>Dear <strong>{user.full_name}</strong>,</p>
                        <p>Your administrator account has been <strong style="color: #dc2626;">suspended</strong> by {current_user.full_name}.</p>
                        <div class="reason-box">
                            <p><strong>Reason for suspension:</strong></p>
                            <p>{reason}</p>
                        </div>
                        <p>You will not be able to access the admin portal until your account is reactivated.</p>
                        <p>If you believe this was done in error, please contact the system administrator.</p>
                        <p>Best regards,<br>
                        <strong>Meru Central Dairy Team</strong></p>
                    </div>
                    <div class="footer">
                        <p>Meru Central Dairy Co-operative Union Ltd</p>
                        <p>P.O. Box 2919, Meru-Kenya | Tel: 0710 901376</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text = f"""
            Account Suspended
            
            Dear {user.full_name},
            
            Your administrator account has been suspended by {current_user.full_name}.
            
            Reason: {reason}
            
            You will not be able to access the admin portal until your account is reactivated.
            
            If you believe this was done in error, please contact the system administrator.
            
            Best regards,
            Meru Central Dairy Team
            """
            
            email_service.send_email_via_smtp(user.email, subject, html, text)
            print(f"✅ Suspension email sent to {user.email}")
        except Exception as e:
            print(f"❌ Failed to send suspension email: {e}")
        
        # Log activity
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='suspend',
            resource_type='user',
            resource_id=user.id,
            description=f'Suspended user: {user.email}. Reason: {reason}'
        )
        
        return jsonify({'message': 'User suspended successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in suspend_user: {e}")
        return jsonify({'error': str(e)}), 500

# ========== ACTIVATE USER (with email) ==========
@user_mgmt_bp.route('/admin/users/<int:user_id>/activate', methods=['POST'])
@login_required
@super_admin_required
def activate_user(user_id):
    """Activate a suspended user - Super Admin only"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Check if already active
        if user.is_active:
            return jsonify({'error': 'User is already active'}), 400
        
        # Activate the user
        user.is_active = True
        db.session.commit()
        
        # ========== SEND ACTIVATION EMAIL ==========
        try:
            frontend_url = current_app.config.get('FRONTEND_URL', 'https://propeller-outclass-parsnip.ngrok-free.dev')
            login_url = f"{frontend_url}/admin/login"
            
            subject = f"Account Reactivated - Meru Dairy Admin Portal"
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Account Reactivated</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #10b981; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ padding: 30px; background: #f9fafb; }}
                    .button {{ display: inline-block; padding: 12px 30px; background: #1e3a8a; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #ddd; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Account Reactivated</h2>
                    </div>
                    <div class="content">
                        <p>Dear <strong>{user.full_name}</strong>,</p>
                        <p>Your administrator account has been <strong style="color: #10b981;">reactivated</strong> by {current_user.full_name}.</p>
                        <p>You can now log in to the admin portal again.</p>
                        <p style="text-align: center;">
                            <a href="{login_url}" class="button">Login to Admin Portal</a>
                        </p>
                        <p>If you have any questions, please contact the system administrator.</p>
                        <p>Best regards,<br>
                        <strong>Meru Central Dairy Team</strong></p>
                    </div>
                    <div class="footer">
                        <p>Meru Central Dairy Co-operative Union Ltd</p>
                        <p>P.O. Box 2919, Meru-Kenya | Tel: 0710 901376</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text = f"""
            Account Reactivated
            
            Dear {user.full_name},
            
            Your administrator account has been reactivated by {current_user.full_name}.
            
            You can now log in to the admin portal at: {login_url}
            
            If you have any questions, please contact the system administrator.
            
            Best regards,
            Meru Central Dairy Team
            """
            
            email_service.send_email_via_smtp(user.email, subject, html, text)
            print(f"✅ Activation email sent to {user.email}")
        except Exception as e:
            print(f"❌ Failed to send activation email: {e}")
        
        # Log activity
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='activate',
            resource_type='user',
            resource_id=user.id,
            description=f'Activated user: {user.email}'
        )
        
        return jsonify({'message': 'User activated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in activate_user: {e}")
        return jsonify({'error': str(e)}), 500


# ========== RESET USER PASSWORD ==========
@user_mgmt_bp.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@super_admin_required
def reset_user_password(user_id):
    """Reset user password - Super Admin only"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Generate new random password
        new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        user.set_password(new_password)
        db.session.commit()
        
        # ========== SEND PASSWORD RESET EMAIL ==========
        try:
            frontend_url = current_app.config.get('FRONTEND_URL', 'https://propeller-outclass-parsnip.ngrok-free.dev')
            email_sent = email_service.send_password_reset_email_with_new_password(user, new_password, frontend_url)
            if email_sent:
                print(f"✅ Password reset email sent to {user.email}")
            else:
                print(f"⚠️ Failed to send password reset email to {user.email}")
        except Exception as e:
            print(f"❌ Error sending password reset email: {e}")
        
        # Log activity
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='reset_password',
            resource_type='user',
            resource_id=user.id,
            description=f'Reset password for user: {user.email}'
        )
        
        return jsonify({
            'message': 'Password reset successfully',
            'new_password': new_password
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in reset_user_password: {e}")
        return jsonify({'error': str(e)}), 500