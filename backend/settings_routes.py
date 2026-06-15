# backend/settings_routes.py
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, SystemSetting
from datetime import datetime
import json

settings_bp = Blueprint('settings', __name__)

# ========== GET ALL SETTINGS ==========
@settings_bp.route('/admin/settings', methods=['GET'])
@login_required
def get_all_settings():
    """Get all system settings - Super Admin only"""
    if current_user.role != 'super_admin':
        return jsonify({'error': 'Super admin access required'}), 403
    
    try:
        settings = SystemSetting.query.order_by(SystemSetting.group, SystemSetting.key).all()
        return jsonify([{
            'id': s.id,
            'key': s.key,
            'value': s.value,
            'group': s.group,
            'description': s.description,
            'is_public': s.is_public,
            'updated_at': s.updated_at.isoformat() if s.updated_at else None
        } for s in settings]), 200
    except Exception as e:
        print(f"Error fetching settings: {e}")
        return jsonify([]), 200

# ========== GET SETTINGS BY GROUP ==========
@settings_bp.route('/admin/settings/<group>', methods=['GET'])
@login_required
def get_settings_by_group(group):
    """Get settings by group"""
    if current_user.role != 'super_admin':
        return jsonify({'error': 'Super admin access required'}), 403
    
    try:
        settings = SystemSetting.query.filter_by(group=group).all()
        return jsonify({s.key: s.value for s in settings}), 200
    except Exception as e:
        print(f"Error fetching settings: {e}")
        return jsonify({}), 200

# ========== UPDATE SINGLE SETTING ==========
@settings_bp.route('/admin/settings', methods=['POST'])
@login_required
def update_setting():
    """Update a single setting - Super Admin only"""
    if current_user.role != 'super_admin':
        return jsonify({'error': 'Super admin access required'}), 403
    
    try:
        data = request.json
        key = data.get('key')
        value = data.get('value')
        group = data.get('group', 'general')
        description = data.get('description', '')
        
        setting = SystemSetting.query.filter_by(key=key).first()
        
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = SystemSetting(
                key=key,
                value=value,
                group=group,
                description=description
            )
            db.session.add(setting)
        
        db.session.commit()
        
        return jsonify({'message': 'Setting updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating setting: {e}")
        return jsonify({'error': str(e)}), 500

# ========== BULK UPDATE SETTINGS ==========
@settings_bp.route('/admin/settings/bulk', methods=['PUT'])
@login_required
def bulk_update_settings():
    """Update multiple settings at once - Super Admin only"""
    if current_user.role != 'super_admin':
        return jsonify({'error': 'Super admin access required'}), 403
    
    try:
        data = request.json
        settings_dict = data.get('settings', {})
        group = data.get('group', 'general')
        
        for key, value in settings_dict.items():
            setting = SystemSetting.query.filter_by(key=key).first()
            if setting:
                setting.value = value
                setting.updated_at = datetime.utcnow()
            else:
                setting = SystemSetting(key=key, value=value, group=group)
                db.session.add(setting)
        
        db.session.commit()
        return jsonify({'message': 'Settings updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating settings: {e}")
        return jsonify({'error': str(e)}), 500

# ========== DELETE SETTING ==========
@settings_bp.route('/admin/settings/<int:setting_id>', methods=['DELETE'])
@login_required
def delete_setting(setting_id):
    """Delete a setting - Super Admin only"""
    if current_user.role != 'super_admin':
        return jsonify({'error': 'Super admin access required'}), 403
    
    try:
        setting = SystemSetting.query.get_or_404(setting_id)
        db.session.delete(setting)
        db.session.commit()
        return jsonify({'message': 'Setting deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting setting: {e}")
        return jsonify({'error': str(e)}), 500

# ========== TEST EMAIL CONFIGURATION ==========
# Update the test_email_config function in settings_routes.py

@settings_bp.route('/admin/settings/test-email', methods=['POST'])
@login_required
def test_email_config():
    """Test email configuration - Super Admin only"""
    if current_user.role != 'super_admin':
        return jsonify({'error': 'Super admin access required'}), 403
    
    try:
        # Get test email from request (handle both JSON and form data)
        if request.is_json:
            data = request.get_json()
            test_email = data.get('to', current_user.email) if data else current_user.email
        else:
            test_email = request.form.get('to', current_user.email)
        
        from email_service import email_service
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Email Test</title>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #1e3a8a; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background: #f3f4f6; padding: 10px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Meru Dairy - Email Test</h2>
                </div>
                <div class="content">
                    <p>This is a test email from Meru Dairy System.</p>
                    <p>If you received this email, your email configuration is working correctly.</p>
                    <p><strong>Configuration Details:</strong></p>
                    <ul>
                        <li>SMTP Server: {email_service.smtp_server}</li>
                        <li>SMTP Port: {email_service.smtp_port}</li>
                        <li>From: {email_service.from_email}</li>
                    </ul>
                    <p>Sent at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                </div>
                <div class="footer">
                    <p>Meru Central Dairy Co-operative Union Ltd</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"""
        This is a test email from Meru Dairy System.
        
        If you received this email, your email configuration is working correctly.
        
        Configuration Details:
        - SMTP Server: {email_service.smtp_server}
        - SMTP Port: {email_service.smtp_port}
        - From: {email_service.from_email}
        
        Sent at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
        """
        
        success = email_service._send_email(test_email, "Test Email - Meru Dairy System", html, text)
        
        if success:
            return jsonify({'message': 'Test email sent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send test email. Check SMTP configuration.'}), 500
            
    except Exception as e:
        print(f"Error sending test email: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500