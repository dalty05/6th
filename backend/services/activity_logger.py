from models import db, ActivityLog
from flask import request
from datetime import datetime

def log_activity(user, action, resource_type, resource_id=None, description=None, details=None):
    """
    Log user activity to the database
    
    Args:
        user: User object
        action: String (login, logout, create, update, delete, view, etc.)
        resource_type: String (user, product, blog, tour, booking, etc.)
        resource_id: Integer ID of the resource
        description: String description of the activity
        details: Additional JSON details
    """
    try:
        # Get request context if available
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent')
        
        activity = ActivityLog(
            user_id=user.id,
            user_name=user.full_name,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(activity)
        db.session.commit()
        return True
    except Exception as e:
        return False