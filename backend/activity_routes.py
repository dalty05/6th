

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, ActivityLog
from datetime import datetime, timedelta
import json

activity_bp = Blueprint('activity', __name__)

def log_activity(user_id, user_name, action, resource_type, resource_id, description, details=None):
    """Helper function to log activities"""
    try:
        log = ActivityLog(
            user_id=user_id,
            user_name=user_name,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            details=json.dumps(details) if details else None,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent', '') if request else ''
        )
        db.session.add(log)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error logging activity: {e}")
        db.session.rollback()
        return False


@activity_bp.route('/admin/activities', methods=['GET'])
@login_required
def get_activities():
    """Get user's activities"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # ✅ Check if user has permission to view activities
        from permission_service import has_permission
        if not has_permission(current_user, 'activities', 'read'):
            # Check if user is admin or tour staff
            if current_user.role in ['admin', 'tour_manager', 'tour_assistant']:
                # Allow access for these roles even without explicit permission
                pass
            else:
                return jsonify({'error': 'Permission denied'}), 403
        
        # Different users see different activities
        if current_user.is_super_admin():
            activities = ActivityLog.query.order_by(
                ActivityLog.created_at.desc()
            ).limit(limit).all()
        else:
            activities = ActivityLog.query.filter_by(
                user_id=current_user.id
            ).order_by(
                ActivityLog.created_at.desc()
            ).limit(limit).all()
        
        return jsonify({
            'activities': [a.to_dict() for a in activities]
        }), 200
        
    except Exception as e:
        print(f"Error getting activities: {e}")
        return jsonify({'error': str(e)}), 500



@activity_bp.route('/admin/activities/<int:id>', methods=['GET'])
@login_required
def get_activity(id):
    """Get single activity details"""
    try:
        activity = ActivityLog.query.get_or_404(id)
        return jsonify({
            'id': activity.id,
            'user_name': activity.user_name,
            'action': activity.action,
            'resource_type': activity.resource_type,
            'description': activity.description,
            'details': json.loads(activity.details) if activity.details else None,
            'ip_address': activity.ip_address,
            'created_at': activity.created_at.isoformat() if activity.created_at else None
        }), 200
    except Exception as e:
        print(f"Error in get_activity: {e}")
        return jsonify({'error': 'Activity not found'}), 404