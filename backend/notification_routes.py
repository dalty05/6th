# backend/notification_routes.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, ActivityLog
from datetime import datetime, timedelta








notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    """Get notifications for current user"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        # For now, return activity logs as notifications
        activities = ActivityLog.query.filter_by(user_id=current_user.id)\
            .order_by(ActivityLog.created_at.desc())\
            .limit(limit).all()
        
        notifications = []
        for activity in activities:
            notification_type = 'info'
            if activity.action == 'create':
                notification_type = 'success'
            elif activity.action == 'delete':
                notification_type = 'error'
            elif activity.action == 'update':
                notification_type = 'warning'
            
            notifications.append({
                'id': activity.id,
                'title': f'{activity.action.capitalize()} {activity.resource_type}',
                'message': activity.description,
                'type': notification_type,
                'read': False,  # You can add read status to ActivityLog if needed
                'timestamp': activity.created_at.isoformat(),
                'link': f'/admin/{activity.resource_type}s'
            })
        
        return jsonify(notifications), 200
    except Exception as e:
        import traceback
        print("Error in get_notifications:")
        traceback.print_exc()
        return jsonify([]), 200


@notification_bp.route('/notifications/<int:id>/read', methods=['PUT'])
@login_required
def mark_notification_read(id):
    """Mark a notification as read"""
    # For now, just return success
    # You can add a Notification model later
    return jsonify({'message': 'ok'}), 200

@notification_bp.route('/notifications/read-all', methods=['PUT'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    return jsonify({'message': 'ok'}), 200

@notification_bp.route('/notifications/<int:id>', methods=['DELETE'])
@login_required
def delete_notification(id):
    """Delete a notification"""
    return jsonify({'message': 'ok'}), 200