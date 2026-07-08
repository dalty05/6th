from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from permission_service import get_user_permissions

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/debug/permissions', methods=['GET'])
@login_required
def get_permissions():
    """Get current user's permissions for frontend"""
    try:
        permissions = get_user_permissions(current_user)
        
        return jsonify({
            'permissions': permissions,
            'role': current_user.role,
            'user_id': current_user.id,
            'email': current_user.email,
            'is_authenticated': current_user.is_authenticated
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500