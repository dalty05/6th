

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
    """Get recent activities (admin only)"""
    try:
        if not current_user.is_super_admin() and not current_user.is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        days = request.args.get('days', 30, type=int)
        activity_type = request.args.get('type', None)
        limit = request.args.get('limit', 50, type=int)
        
        query = ActivityLog.query
        
        # Filter by days
        if days and days > 0:
            cutoff = datetime.utcnow() - timedelta(days=days)
            query = query.filter(ActivityLog.created_at >= cutoff)
        
        # Filter by type
        if activity_type:
            query = query.filter(ActivityLog.resource_type == activity_type)
        
        # Order by most recent
        activities = query.order_by(ActivityLog.created_at.desc()).limit(limit).all()
        
        return jsonify([{
            'id': a.id,
            'user_name': a.user_name,
            'action': a.action,
            'resource_type': a.resource_type,
            'description': a.description,
            'details': json.loads(a.details) if a.details else None,
            'ip_address': a.ip_address,
            'created_at': a.created_at.isoformat() if a.created_at else None
        } for a in activities]), 200
    except Exception as e:
        print(f"Error in get_activities: {e}")
        return jsonify([]), 200


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