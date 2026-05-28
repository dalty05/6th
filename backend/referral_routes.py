# backend/referral_routes.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, User, ReferralLink, ReferralClick, ActivityLog
from datetime import datetime, timedelta
import secrets
import string

referral_bp = Blueprint('referral', __name__)

def log_activity(user_id, user_name, action, resource_type, resource_id, description, details=None):
    """Helper function to log activities"""
    import json
    log = ActivityLog(
        user_id=user_id,
        user_name=user_name,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        details=json.dumps(details) if details else None,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', '')
    )
    db.session.add(log)
    db.session.commit()

# ========== REFERRAL LINK CRUD ==========

@referral_bp.route('/referral/links', methods=['GET'])
@login_required
def get_referral_links():
    """Get all referral links for current user"""
    try:
        if current_user.is_super_admin() or current_user.is_admin():
            # Admins can see all links
            links = ReferralLink.query.all()
        else:
            # Partners only see their own links
            links = ReferralLink.query.filter_by(user_id=current_user.id).all()
        
        return jsonify([link.to_dict() for link in links]), 200
    except Exception as e:
        print(f"Error in get_referral_links: {e}")
        return jsonify([]), 200

@referral_bp.route('/referral/links', methods=['POST'])
@login_required
def create_referral_link():
    """Create a new referral link"""
    try:
        data = request.json
        name = data.get('name')
        destination_url = data.get('destination_url', '')
        campaign_name = data.get('campaign_name', '')
        expires_at = data.get('expires_at')
        
        if not name:
            return jsonify({'error': 'Link name is required'}), 400
        
        # Create new link
        link = ReferralLink(
            user_id=current_user.id,
            name=name,
            destination_url=destination_url,
            campaign_name=campaign_name,
            is_active=True
        )
        
        # Generate unique code
        code = f"REF-{current_user.id}-{''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))}"
        link.link_code = code
        
        if expires_at:
            link.expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        
        db.session.add(link)
        db.session.commit()
        
        # Log activity
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='create',
            resource_type='referral',
            resource_id=link.id,
            description=f'Created referral link: {name}'
        )
        
        return jsonify(link.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error in create_referral_link: {e}")
        return jsonify({'error': str(e)}), 500

@referral_bp.route('/referral/links/<int:link_id>', methods=['PUT'])
@login_required
def update_referral_link(link_id):
    """Update a referral link"""
    try:
        link = ReferralLink.query.get_or_404(link_id)
        
        # Check permission
        if link.user_id != current_user.id and not current_user.is_super_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.json
        if 'name' in data:
            link.name = data['name']
        if 'destination_url' in data:
            link.destination_url = data['destination_url']
        if 'campaign_name' in data:
            link.campaign_name = data['campaign_name']
        if 'expires_at' in data and data['expires_at']:
            link.expires_at = datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00'))
        
        db.session.commit()
        
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='update',
            resource_type='referral',
            resource_id=link.id,
            description=f'Updated referral link: {link.name}'
        )
        
        return jsonify(link.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_referral_link: {e}")
        return jsonify({'error': str(e)}), 500

@referral_bp.route('/referral/links/<int:link_id>', methods=['DELETE'])
@login_required
def delete_referral_link(link_id):
    """Delete a referral link"""
    try:
        link = ReferralLink.query.get_or_404(link_id)
        
        # Check permission
        if link.user_id != current_user.id and not current_user.is_super_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        link_name = link.name
        db.session.delete(link)
        db.session.commit()
        
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='delete',
            resource_type='referral',
            resource_id=link_id,
            description=f'Deleted referral link: {link_name}'
        )
        
        return jsonify({'message': 'Link deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_referral_link: {e}")
        return jsonify({'error': str(e)}), 500

@referral_bp.route('/referral/links/<int:link_id>/status', methods=['PUT'])
@login_required
def toggle_link_status(link_id):
    """Toggle referral link active status"""
    try:
        link = ReferralLink.query.get_or_404(link_id)
        
        if link.user_id != current_user.id and not current_user.is_super_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.json
        link.is_active = data.get('is_active', False)
        db.session.commit()
        
        status = 'activated' if link.is_active else 'deactivated'
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='update',
            resource_type='referral',
            resource_id=link.id,
            description=f'{status} referral link: {link.name}'
        )
        
        return jsonify({'message': f'Link {status}'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in toggle_link_status: {e}")
        return jsonify({'error': str(e)}), 500

# ========== REFERRAL STATS ==========

@referral_bp.route('/referral/stats', methods=['GET'])
@login_required
def get_referral_stats():
    """Get referral statistics for current user"""
    try:
        if current_user.is_super_admin() or current_user.is_admin():
            # Admins see all stats
            links = ReferralLink.query.all()
            total_clicks = sum(l.total_clicks for l in links)
            unique_clicks = sum(l.unique_clicks for l in links)
            conversions = sum(l.conversions for l in links)
        else:
            # Partners only see their own
            links = ReferralLink.query.filter_by(user_id=current_user.id).all()
            total_clicks = current_user.total_clicks or 0
            unique_clicks = sum(l.unique_clicks for l in links)
            conversions = current_user.total_conversions or 0
        
        conversion_rate = round((conversions / total_clicks * 100), 2) if total_clicks > 0 else 0
        
        return jsonify({
            'totalClicks': total_clicks,
            'uniqueClicks': unique_clicks,
            'totalConversions': conversions,
            'conversionRate': conversion_rate,
            'clickTrend': 12  # Example trend data
        }), 200
    except Exception as e:
        print(f"Error in get_referral_stats: {e}")
        return jsonify({
            'totalClicks': 0,
            'uniqueClicks': 0,
            'totalConversions': 0,
            'conversionRate': 0
        }), 200

@referral_bp.route('/referral/recent', methods=['GET'])
@login_required
def get_recent_referrals():
    """Get recent referral links"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        if current_user.is_super_admin() or current_user.is_admin():
            links = ReferralLink.query.order_by(ReferralLink.created_at.desc()).limit(limit).all()
        else:
            links = ReferralLink.query.filter_by(user_id=current_user.id)\
                .order_by(ReferralLink.created_at.desc()).limit(limit).all()
        
        return jsonify([link.to_dict() for link in links]), 200
    except Exception as e:
        print(f"Error in get_recent_referrals: {e}")
        return jsonify([]), 200


@referral_bp.route('/referral/top-links', methods=['GET'])
@login_required
def get_top_links():
    """Get top performing referral links"""
    try:
        limit = request.args.get('limit', 5, type=int)
        limit = max(1, min(50, limit))

        if current_user.is_super_admin() or current_user.is_admin():
            links = ReferralLink.query.order_by(ReferralLink.total_clicks.desc()).limit(limit).all()
        else:
            links = (
                ReferralLink.query.filter_by(user_id=current_user.id)
                .order_by(ReferralLink.total_clicks.desc())
                .limit(limit)
                .all()
            )

        return jsonify([link.to_dict() for link in links]), 200
    except Exception as e:
        print(f"Error in get_top_links: {e}")
        return jsonify([]), 200


@referral_bp.route('/referral/analytics', methods=['GET'])
@login_required
def get_referral_analytics():
    """Get detailed referral analytics with chart data"""
    try:
        days = request.args.get('days', 30, type=int)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get clicks data for chart
        if current_user.is_super_admin() or current_user.is_admin():
            clicks = ReferralClick.query.filter(
                ReferralClick.clicked_at >= start_date,
                ReferralClick.clicked_at <= end_date
            ).all()
            links = ReferralLink.query.all()
        else:
            user_link_ids = [l.id for l in ReferralLink.query.filter_by(user_id=current_user.id).all()]
            clicks = ReferralClick.query.filter(
                ReferralClick.link_id.in_(user_link_ids),
                ReferralClick.clicked_at >= start_date,
                ReferralClick.clicked_at <= end_date
            ).all()
            links = ReferralLink.query.filter_by(user_id=current_user.id).all()
        
        # Prepare chart data
        chart_data = []
        for i in range(days):
            date = end_date - timedelta(days=days - i - 1)
            day_clicks = sum(1 for c in clicks if c.clicked_at.date() == date.date())
            day_conversions = sum(1 for c in clicks if c.converted and c.clicked_at.date() == date.date())
            chart_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'clicks': day_clicks,
                'conversions': day_conversions
            })
        
        total_clicks = sum(l.total_clicks for l in links)
        unique_clicks = sum(l.unique_clicks for l in links)
        conversions = sum(l.conversions for l in links)
        conversion_rate = round((conversions / total_clicks * 100), 2) if total_clicks > 0 else 0
        
        # Get top links
        top_links = sorted(links, key=lambda l: l.total_clicks, reverse=True)[:5]
        
        return jsonify({
            'stats': {
                'totalClicks': total_clicks,
                'uniqueClicks': unique_clicks,
                'totalConversions': conversions,
                'conversionRate': conversion_rate
            },
            'chartData': {
                'labels': [d['date'] for d in chart_data],
                'clicks': [d['clicks'] for d in chart_data],
                'conversions': [d['conversions'] for d in chart_data]
            },
            'topLinks': [link.to_dict() for link in top_links]
        }), 200
    except Exception as e:
        print(f"Error in get_referral_analytics: {e}")
        return jsonify({
            'stats': {'totalClicks': 0, 'uniqueClicks': 0, 'totalConversions': 0, 'conversionRate': 0},
            'chartData': {'labels': [], 'clicks': [], 'conversions': []},
            'topLinks': []
        }), 200

@referral_bp.route('/referral/partner/<int:user_id>/stats', methods=['GET'])
@login_required
def get_partner_stats(user_id):
    """Get stats for a specific partner (admin only)"""
    if not current_user.is_super_admin() and not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        links = ReferralLink.query.filter_by(user_id=user_id).all()
        
        stats = {
            'totalClicks': user.total_clicks or 0,
            'uniqueClicks': sum(l.unique_clicks for l in links),
            'totalConversions': user.total_conversions or 0,
            'conversionRate': round((user.total_conversions or 0) / (user.total_clicks or 1) * 100, 2)
        }
        
        return jsonify({
            'stats': stats,
            'links': [link.to_dict() for link in links]
        }), 200
    except Exception as e:
        print(f"Error in get_partner_stats: {e}")
        return jsonify({'stats': {}, 'links': []}), 200