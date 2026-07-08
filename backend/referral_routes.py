# backend/referral_routes.py
from flask import Blueprint, request, jsonify, redirect, render_template_string
from flask_login import login_required, current_user
from models import db, User, ReferralLink, ReferralClick, ActivityLog
from datetime import datetime, timedelta
import secrets
import string
import json
from sqlalchemy import func, and_


from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, ReferralLink, ReferralClick, User
from datetime import datetime
import secrets
import re


from flask import redirect






referral_bp = Blueprint('referral', __name__)

def log_activity(user_id, user_name, action, resource_type, resource_id, description):
    try:
        log = ActivityLog(
            user_id=user_id,
            user_name=user_name,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")
        db.session.rollback()

# ========== REFERRAL LINK CRUD ==========

@referral_bp.route('/referral/links', methods=['GET'])
@login_required
def get_referral_links():
    """Get all referral links for current user"""
    try:
        # Admin sees all, regular users see only theirs
        if current_user.role == 'super_admin':
            links = ReferralLink.query.order_by(ReferralLink.created_at.desc()).all()
        else:
            links = ReferralLink.query.filter_by(user_id=current_user.id)\
                .order_by(ReferralLink.created_at.desc()).all()
        
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        
        return jsonify([{
            'id': l.id,
            'name': l.name,
            'link_code': l.link_code, 
            'full_url': f"{frontend_url}/r/{l.link_code}",
            'destination_url': l.destination_url,
            'campaign_name': l.campaign_name,
            'is_active': l.is_active,
            'total_clicks': l.total_clicks,
            'unique_clicks': l.unique_clicks,
            'conversions': l.conversions,
            'created_at': l.created_at.isoformat(),
            'user_name': l.user.full_name if l.user else None
        } for l in links]), 200
        
    except Exception as e:
        print(f"Error fetching referral links: {e}")
        return jsonify([]), 200


@referral_bp.route('/referral/links', methods=['POST'])
@login_required

def create_referral_link():
    """Create a new referral link with PARTNER-{id}-{code} format"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        destination_url = current_app.config.get('REFERRAL_DESTINATION_URL', 'https://shop.mountkenyamilk.co.ke/')


        campaign_name = data.get('campaign_name', '').strip()

        
        # Validate
        if not name:
            return jsonify({'error': 'Link name is required'}), 400
        if not destination_url:
            
            destination_url = 'https://shop.mountkenyamilk.co.ke/'
        
        # Validate URL format
        if not re.match(r'^https?://', destination_url):
            destination_url = 'https://' + destination_url
        
        
        import secrets
        random_part = secrets.token_urlsafe(4).upper().replace('-', '')
        link_code = f"PARTNER-{current_user.id}-{random_part}"
        
        # Create link
        link = ReferralLink(
            user_id=current_user.id,
            link_code=link_code,
            name=name,
            destination_url=destination_url,
            campaign_name=campaign_name,
            is_active=True,
            total_clicks=0,
            unique_clicks=0,
            conversions=0,
            created_at=datetime.utcnow()
        )
        
        db.session.add(link)
        db.session.commit()
        
      
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173/')
        full_url = f"{frontend_url}/r/{link_code}"
        
        return jsonify({
            'message': 'Referral link created',
            'link': {
                'id': link.id,
                'name': link.name,
                'link_code': link.link_code,
                'full_url': full_url,
                'destination_url': link.destination_url,
                'campaign_name': link.campaign_name,
                'is_active': link.is_active,
                'total_clicks': link.total_clicks,
                'unique_clicks': link.unique_clicks,
                'conversions': link.conversions,
                'created_at': link.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating referral link: {e}")
        return jsonify({'error': str(e)}), 500

@referral_bp.route('/referral/links/<int:link_id>', methods=['PUT'])
@login_required
def update_referral_link(link_id):
    
    try:
        link = ReferralLink.query.get_or_404(link_id)
        
        
        if current_user.role != 'super_admin' and link.user_id != current_user.id:
            return jsonify({'error': 'Permission denied'}), 403
        
        data = request.json
        
        if 'name' in data:
            link.name = data['name']
        if 'destination_url' in data:
            url = data['destination_url']
            if not re.match(r'^https?://', url):
                url = 'https://' + url
            link.destination_url = url
        if 'campaign_name' in data:
            link.campaign_name = data['campaign_name']
        if 'is_active' in data:
            link.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({'message': 'Referral link updated'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500





# ========== RECORD CONVERSION ==========
@referral_bp.route('/referral/links/<int:link_id>/convert', methods=['POST'])
@login_required
def record_conversion(link_id):
    try:
        link = ReferralLink.query.get_or_404(link_id)
        
        # Check permission
        if current_user.role != 'super_admin' and link.user_id != current_user.id:
            return jsonify({'error': 'Permission denied'}), 403
        
        link.conversions += 1
        db.session.commit()
        
        return jsonify({'message': 'Conversion recorded', 'total_conversions': link.conversions}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========== DELETE REFERRAL LINK ==========
@referral_bp.route('/referral/links/<int:link_id>', methods=['DELETE'])
@login_required
def delete_referral_link(link_id):
    """Delete a referral link (soft delete)"""
    try:
        link = ReferralLink.query.get_or_404(link_id)
        
        # Check permission
        if current_user.role != 'super_admin' and link.user_id != current_user.id:
            return jsonify({'error': 'Permission denied'}), 403
        
        db.session.delete(link)
        db.session.commit()
        
        return jsonify({'message': 'Referral link deleted'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



@referral_bp.route('/referral/links/<int:link_id>/toggle', methods=['POST'])
@login_required
def toggle_link_status(link_id):
    """Toggle referral link active status"""
    try:
        link = ReferralLink.query.get_or_404(link_id)
        
        if link.user_id != current_user.id and not current_user.is_super_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        link.is_active = not link.is_active
        db.session.commit()
        
        status = 'activated' if link.is_active else 'deactivated'
        log_activity(
            current_user.id, current_user.full_name,
            'update', 'referral', link.id, f'{status} referral link: {link.name}'
        )
        
        return jsonify({'message': f'Link {status}', 'is_active': link.is_active}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in toggle_link_status: {e}")
        return jsonify({'error': str(e)}), 500

# ========== REFERRAL TRACKING (Public) ==========


@referral_bp.route('/r/<path:link_code>', methods=['GET'])
def track_referral_click(link_code):
    """Track clicks on referral links and redirect to destination"""
    try:
        from flask import redirect, request, jsonify
        from models import ReferralLink, ReferralClick, User
        from datetime import datetime
        
        link = None
        
        # Method 1: Direct match with link_code in database
        link = ReferralLink.query.filter_by(link_code=link_code, is_active=True).first()
        
        # Method 2: Parse PARTNER-{user_id}-{random} format
        if not link and link_code.startswith('PARTNER-'):
            parts = link_code.split('-')
            if len(parts) >= 3:
                try:
                    user_id = int(parts[1])
                    # Find the most recent active link for this user
                    link = ReferralLink.query.filter_by(
                        user_id=user_id, 
                        is_active=True
                    ).order_by(ReferralLink.created_at.desc()).first()
                except ValueError:
                    pass
        
        # Method 3: Try to find by user_id only (if code is just user ID)
        if not link:
            try:
                user_id = int(link_code)
                link = ReferralLink.query.filter_by(
                    user_id=user_id, 
                    is_active=True
                ).order_by(ReferralLink.created_at.desc()).first()
            except ValueError:
                pass
        
        # Method 4: Try partial match (search all active links)
        if not link:
            link = ReferralLink.query.filter_by(is_active=True).first()
        
        if not link:
            print(f"Referral link not found for code: {link_code}")
            return jsonify({'error': 'Invalid referral link'}), 404
        
        # Get client information
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        referrer_url = request.headers.get('Referer', '')
        
        # Check if this IP has clicked this link before (for unique count)
        existing_click = ReferralClick.query.filter_by(
            link_id=link.id,
            ip_address=ip_address
        ).first()
        
        is_unique = (existing_click is None)
        
        # Record the click
        click = ReferralClick(
            link_id=link.id,
            ip_address=ip_address,
            user_agent=user_agent[:500],
            referrer_url=referrer_url[:500] if referrer_url else None,
            converted=False,
            clicked_at=datetime.utcnow()
        )
        
        db.session.add(click)
        
        # Update link statistics
        link.total_clicks += 1
        if is_unique:
            link.unique_clicks += 1
        
        db.session.commit()
        
        print(f"✅ Referral tracked: {link_code} -> {link.destination_url} (Click #{link.total_clicks})")
        
        # Redirect to destination
        return redirect(link.destination_url)
        
    except Exception as e:
        db.session.rollback()
        print(f"Error tracking referral: {e}")
        import traceback
        traceback.print_exc()
        
        # Still try to redirect even if tracking failed
        if 'link' in locals() and link and link.destination_url:
            return redirect(link.destination_url)
        
        return jsonify({'error': 'Server error'}), 500



# ========== ENHANCED ANALYTICS ENDPOINTS ==========
@referral_bp.route('/referral/stats', methods=['GET'])
@login_required
def get_overall_stats():
    """Get overall referral statistics - accessible to all authenticated users"""
    # Remove the super admin check, just show what the user can see
    if current_user.role == 'super_admin':
        total_links = ReferralLink.query.count()
        total_clicks = db.session.query(db.func.sum(ReferralLink.total_clicks)).scalar() or 0
        total_unique = db.session.query(db.func.sum(ReferralLink.unique_clicks)).scalar() or 0
        total_conversions = db.session.query(db.func.sum(ReferralLink.conversions)).scalar() or 0
        active_links = ReferralLink.query.filter_by(is_active=True).count()
    else:
        # Regular users only see their own stats
        total_links = ReferralLink.query.filter_by(user_id=current_user.id).count()
        total_clicks = db.session.query(db.func.sum(ReferralLink.total_clicks)).filter_by(user_id=current_user.id).scalar() or 0
        total_unique = db.session.query(db.func.sum(ReferralLink.unique_clicks)).filter_by(user_id=current_user.id).scalar() or 0
        total_conversions = db.session.query(db.func.sum(ReferralLink.conversions)).filter_by(user_id=current_user.id).scalar() or 0
        active_links = ReferralLink.query.filter_by(user_id=current_user.id, is_active=True).count()
    
    return jsonify({
        'total_links': total_links,
        'total_clicks': total_clicks,
        'total_unique_clicks': total_unique,
        'total_conversions': total_conversions,
        'active_links': active_links
    }), 200
@referral_bp.route('/referral/top-links', methods=['GET'])

def get_top_links():
    """Get top performing links"""
    limit = request.args.get('limit', 3, type=int)
    sort_by = request.args.get('sort_by', 'clicks')
    
    if sort_by == 'clicks':
        order_by = ReferralLink.total_clicks.desc()
    else:
        order_by = ReferralLink.conversions.desc()
    
    links = ReferralLink.query.filter_by(is_active=True)\
        .order_by(order_by)\
        .limit(limit).all()
    
    return jsonify([{
        'id': l.id,
        'name': l.name,
        'code': l.link_code,
        'clicks': l.total_clicks,
        'unique_clicks': l.unique_clicks,
        'conversions': l.conversions,
        'partner_name': l.user.full_name if l.user else None
    } for l in links]), 200

@referral_bp.route('/referral/analytics/daily', methods=['GET'])
@login_required
def get_daily_analytics():
    """Get daily breakdown of clicks and conversions"""
    try:
        days = request.args.get('days', 30, type=int)
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        if current_user.is_super_admin() or current_user.is_admin():
            links = ReferralLink.query.all()
        else:
            links = ReferralLink.query.filter_by(user_id=current_user.id).all()
        
        link_ids = [l.id for l in links] if links else []
        
        # Get daily aggregations
        daily_stats = db.session.query(
            func.date(ReferralClick.clicked_at).label('date'),
            func.count(ReferralClick.id).label('clicks'),
            func.sum(func.cast(ReferralClick.converted, db.Integer)).label('conversions')
        ).filter(
            ReferralClick.link_id.in_(link_ids),
            ReferralClick.clicked_at >= start_date
        ).group_by(func.date(ReferralClick.clicked_at)).all() if link_ids else []
        
        # Create full date range
        result = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            day_stats = next((d for d in daily_stats if d.date.strftime('%Y-%m-%d') == date_str), None)
            result.append({
                'date': date_str,
                'clicks': day_stats.clicks if day_stats else 0,
                'conversions': day_stats.conversions if day_stats else 0
            })
            current_date += timedelta(days=1)
        
        return jsonify(result), 200
    except Exception as e:
        print(f"Error in get_daily_analytics: {e}")
        return jsonify([]), 200

@referral_bp.route('/referral/analytics/sources', methods=['GET'])
@login_required
def get_source_analytics():
    """Get click sources breakdown (referrer URLs)"""
    try:
        if current_user.is_super_admin() or current_user.is_admin():
            links = ReferralLink.query.all()
        else:
            links = ReferralLink.query.filter_by(user_id=current_user.id).all()
        
        link_ids = [l.id for l in links] if links else []
        
        # Get source breakdown
        source_stats = db.session.query(
            ReferralClick.referrer_url,
            func.count(ReferralClick.id).label('count')
        ).filter(
            ReferralClick.link_id.in_(link_ids)
        ).group_by(ReferralClick.referrer_url).all() if link_ids else []
        
        # Categorize sources
        sources = {
            'direct': 0,
            'facebook': 0,
            'twitter': 0,
            'instagram': 0,
            'linkedin': 0,
            'whatsapp': 0,
            'email': 0,
            'other': 0
        }
        
        for stat in source_stats:
            url = stat.referrer_url or ''
            count = stat.count
            
            if 'facebook.com' in url or 'fb.com' in url:
                sources['facebook'] += count
            elif 'twitter.com' in url or 'x.com' in url:
                sources['twitter'] += count
            elif 'instagram.com' in url:
                sources['instagram'] += count
            elif 'linkedin.com' in url:
                sources['linkedin'] += count
            elif 'whatsapp.com' in url or 'wa.me' in url:
                sources['whatsapp'] += count
            elif 'mail.' in url or 'email' in url:
                sources['email'] += count
            elif url == '' or url is None:
                sources['direct'] += count
            else:
                sources['other'] += count
        
        return jsonify(sources), 200
    except Exception as e:
        print(f"Error in get_source_analytics: {e}")
        return jsonify({}), 200

@referral_bp.route('/referral/analytics/geo', methods=['GET'])
@login_required
def get_geo_analytics():
    """Get geographical distribution (based on IP - simplified)"""
    try:
        if current_user.is_super_admin() or current_user.is_admin():
            links = ReferralLink.query.all()
        else:
            links = ReferralLink.query.filter_by(user_id=current_user.id).all()
        
        link_ids = [l.id for l in links] if links else []
        
        

        
        ip_stats = db.session.query(
            ReferralClick.ip_address,
            func.count(ReferralClick.id).label('count')
        ).filter(
            ReferralClick.link_id.in_(link_ids)
        ).group_by(ReferralClick.ip_address).limit(20).all() if link_ids else []
        
        return jsonify([{
            'ip': stat.ip_address,
            'count': stat.count
        } for stat in ip_stats]), 200
    except Exception as e:
        print(f"Error in get_geo_analytics: {e}")
        return jsonify([]), 200

@referral_bp.route('/referral/analytics/timeline', methods=['GET'])
@login_required
def get_timeline_analytics():
    """Get hourly timeline for today"""
    try:
        today = datetime.utcnow().date()
        start_of_day = datetime(today.year, today.month, today.day)
        
        if current_user.is_super_admin() or current_user.is_admin():
            links = ReferralLink.query.all()
        else:
            links = ReferralLink.query.filter_by(user_id=current_user.id).all()
        
        link_ids = [l.id for l in links] if links else []
        
        # Get hourly breakdown
        hourly_stats = db.session.query(
            func.strftime('%H', ReferralClick.clicked_at).label('hour'),
            func.count(ReferralClick.id).label('clicks')
        ).filter(
            ReferralClick.link_id.in_(link_ids),
            ReferralClick.clicked_at >= start_of_day
        ).group_by('hour').all() if link_ids else []
        
        # Create 24-hour array
        result = []
        for hour in range(24):
            hour_str = f"{hour:02d}"
            stat = next((s for s in hourly_stats if s.hour == hour_str), None)
            result.append({
                'hour': hour,
                'clicks': stat.clicks if stat else 0
            })
        
        return jsonify(result), 200
    except Exception as e:
        print(f"Error in get_timeline_analytics: {e}")
        return jsonify([]), 200

@referral_bp.route('/referral/analytics/recent-clicks', methods=['GET'])
@login_required
def get_recent_clicks_analytics():
    """Get recent clicks with details"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        if current_user.is_super_admin() or current_user.is_admin():
            clicks = ReferralClick.query.order_by(ReferralClick.clicked_at.desc()).limit(limit).all()
        else:
            user_link_ids = [l.id for l in ReferralLink.query.filter_by(user_id=current_user.id).all()]
            if user_link_ids:
                clicks = ReferralClick.query.filter(ReferralClick.link_id.in_(user_link_ids))\
                    .order_by(ReferralClick.clicked_at.desc()).limit(limit).all()
            else:
                clicks = []
        
        return jsonify([{
            'id': c.id,
            'ip_address': c.ip_address,
            'referrer_url': c.referrer_url or 'Direct',
            'converted': c.converted,
            'clicked_at': c.clicked_at.isoformat() if c.clicked_at else None,
            'link_name': c.link.name if c.link else 'Unknown',
            'device': 'Desktop'  # Would need user agent parsing for real data
        } for c in clicks]), 200
    except Exception as e:
        print(f"Error in get_recent_clicks_analytics: {e}")
        return jsonify([]), 200

@referral_bp.route('/referral/analytics/summary', methods=['GET'])
@login_required
def get_analytics_summary():
    """Get comprehensive analytics summary"""
    try:
        days = request.args.get('days', 30, type=int)
        
        if current_user.is_super_admin() or current_user.is_admin():
            links = ReferralLink.query.all()
        else:
            links = ReferralLink.query.filter_by(user_id=current_user.id).all()
        
        link_ids = [l.id for l in links] if links else []
        
        # Current period
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        current_clicks = ReferralClick.query.filter(
            ReferralClick.link_id.in_(link_ids),
            ReferralClick.clicked_at >= start_date
        ).count() if link_ids else 0
        
        current_conversions = ReferralClick.query.filter(
            ReferralClick.converted == True,
            ReferralClick.link_id.in_(link_ids),
            ReferralClick.clicked_at >= start_date
        ).count() if link_ids else 0
        
        # Previous period for comparison
        prev_start = start_date - timedelta(days=days)
        prev_clicks = ReferralClick.query.filter(
            ReferralClick.link_id.in_(link_ids),
            ReferralClick.clicked_at >= prev_start,
            ReferralClick.clicked_at < start_date
        ).count() if link_ids else 0
        
        prev_conversions = ReferralClick.query.filter(
            ReferralClick.converted == True,
            ReferralClick.link_id.in_(link_ids),
            ReferralClick.clicked_at >= prev_start,
            ReferralClick.clicked_at < start_date
        ).count() if link_ids else 0
        
        # Unique visitors (unique IPs)
        unique_visitors = db.session.query(func.count(func.distinct(ReferralClick.ip_address))).filter(
            ReferralClick.link_id.in_(link_ids),
            ReferralClick.clicked_at >= start_date
        ).scalar() if link_ids else 0
        
        # Average clicks per link
        avg_clicks = round(current_clicks / len(links), 2) if links else 0
        
        return jsonify({
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            },
            'current': {
                'clicks': current_clicks,
                'conversions': current_conversions,
                'unique_visitors': unique_visitors,
                'conversion_rate': round((current_conversions / current_clicks * 100), 2) if current_clicks > 0 else 0
            },
            'previous': {
                'clicks': prev_clicks,
                'conversions': prev_conversions,
                'conversion_rate': round((prev_conversions / prev_clicks * 100), 2) if prev_clicks > 0 else 0
            },
            'growth': {
                'clicks': round(((current_clicks - prev_clicks) / prev_clicks * 100), 1) if prev_clicks > 0 else 0,
                'conversions': round(((current_conversions - prev_conversions) / prev_conversions * 100), 1) if prev_conversions > 0 else 0
            },
            'averages': {
                'clicks_per_link': avg_clicks,
                'clicks_per_day': round(current_clicks / days, 1) if days > 0 else 0
            },
            'total_links': len(links),
            'active_links': sum(1 for l in links if l.is_active)
        }), 200
    except Exception as e:
        print(f"Error in get_analytics_summary: {e}")
        return jsonify({'error': str(e)}), 500



@referral_bp.route('/referral/links/<int:link_id>/clicks', methods=['GET'])
@login_required
def get_click_analytics(link_id):
    """Get detailed click analytics for a specific link"""
    try:
        link = ReferralLink.query.get_or_404(link_id)
        
        # Check permission
        if current_user.role != 'super_admin' and link.user_id != current_user.id:
            return jsonify({'error': 'Permission denied'}), 403
        
        # Get date range (default: last 30 days)
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        from datetime import timedelta
        start_date = start_date - timedelta(days=days)
        
        # Get clicks with date filter
        clicks = ReferralClick.query.filter(
            ReferralClick.link_id == link_id,
            ReferralClick.clicked_at >= start_date
        ).order_by(ReferralClick.clicked_at.desc()).all()
        
        # Calculate daily stats
        daily_stats = {}
        for click in clicks:
            date_key = click.clicked_at.strftime('%Y-%m-%d')
            if date_key not in daily_stats:
                daily_stats[date_key] = {'clicks': 0, 'unique_ips': set()}
            daily_stats[date_key]['clicks'] += 1
            daily_stats[date_key]['unique_ips'].add(click.ip_address)
        
        # Convert to list for JSON
        daily_data = [{
            'date': date,
            'clicks': data['clicks'],
            'unique_clicks': len(data['unique_ips'])
        } for date, data in sorted(daily_stats.items())]
        
        # Get top referrers
        referrer_stats = {}
        for click in clicks:
            ref = click.referrer_url or 'Direct'
            referrer_stats[ref] = referrer_stats.get(ref, 0) + 1
        
        top_referrers = [{'source': k, 'clicks': v} for k, v in 
                        sorted(referrer_stats.items(), key=lambda x: x[1], reverse=True)[:10]]
        
        return jsonify({
            'link': {
                'id': link.id,
                'name': link.name,
                'total_clicks': link.total_clicks,
                'unique_clicks': link.unique_clicks,
                'conversions': link.conversions
            },
            'summary': {
                'period_days': days,
                'clicks_in_period': len(clicks),
                'unique_in_period': len(set(c.ip_address for c in clicks)),
                'start_date': start_date.isoformat()
            },
            'daily_breakdown': daily_data,
            'top_referrers': top_referrers,
            'recent_clicks': [{
                'ip': c.ip_address,
                'clicked_at': c.clicked_at.isoformat(),
                'referrer': c.referrer_url,
                'user_agent': c.user_agent[:100]
            } for c in clicks[:20]]
        }), 200
        
    except Exception as e:
        print(f"Error fetching analytics: {e}")
        return jsonify({'error': str(e)}), 500





# ========== REGULAR ENDPOINTS (Keep existing) ==========

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
        
        return jsonify([{
            'id': l.id,
            'name': l.name,
            'link_code': l.link_code,
            'total_clicks': l.total_clicks,
            'unique_clicks': l.unique_clicks,
            'conversions': l.conversions,
            'conversion_rate': round((l.conversions / l.total_clicks * 100), 2) if l.total_clicks > 0 else 0,
            'created_at': l.created_at.isoformat() if l.created_at else None
        } for l in links]), 200
    except Exception as e:
        print(f"Error in get_recent_referrals: {e}")
        return jsonify([]), 200

@referral_bp.route('/referral/analytics', methods=['GET'])
@login_required
def get_referral_analytics():
    """Get detailed referral analytics with chart data"""
    try:
        days = request.args.get('days', 30, type=int)
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        if current_user.is_super_admin() or current_user.is_admin():
            links = ReferralLink.query.all()
        else:
            links = ReferralLink.query.filter_by(user_id=current_user.id).all()
        
        link_ids = [l.id for l in links] if links else []
        
        clicks = ReferralClick.query.filter(
            ReferralClick.link_id.in_(link_ids),
            ReferralClick.clicked_at >= start_date,
            ReferralClick.clicked_at <= end_date
        ).all() if link_ids else []
        
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
            'topLinks': [{
                'id': l.id,
                'name': l.name,
                'link_code': l.link_code,
                'total_clicks': l.total_clicks,
                'conversion_rate': round((l.conversions / l.total_clicks * 100), 2) if l.total_clicks > 0 else 0
            } for l in top_links]
        }), 200
    except Exception as e:
        print(f"Error in get_referral_analytics: {e}")
        return jsonify({
            'stats': {'totalClicks': 0, 'uniqueClicks': 0, 'totalConversions': 0, 'conversionRate': 0},
            'chartData': {'labels': [], 'clicks': [], 'conversions': []},
            'topLinks': []
        }), 200



# ========== GET PARTNER STATS (matches frontend) ==========
@referral_bp.route('/referral/partner/<int:user_id>/stats', methods=['GET'])
@login_required
def get_partner_stats(user_id):
    """Get stats for specific partner"""
    # Check permission
    if current_user.role != 'super_admin' and current_user.id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    links = ReferralLink.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'partner_id': user_id,
        'total_links': len(links),
        'total_clicks': sum(l.total_clicks for l in links),
        'total_unique_clicks': sum(l.unique_clicks for l in links),
        'total_conversions': sum(l.conversions for l in links),
        'links': [{
            'id': l.id,
            'name': l.name,
            'code': l.link_code,
            'clicks': l.total_clicks,
            'unique_clicks': l.unique_clicks,
            'conversions': l.conversions,
            'is_active': l.is_active
        } for l in links]
    }), 200

@referral_bp.route('/referral/admin/links/<int:link_id>/toggle-status', methods=['PUT'])
@login_required
def admin_toggle_link_status(link_id):
    """Super admin only: Suspend or activate any referral link"""
    if current_user.role != 'super_admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        link = ReferralLink.query.get_or_404(link_id)
        data = request.json
        is_active = data.get('is_active', False)
        
        link.is_active = is_active
        db.session.commit()
        
        status = "activated" if is_active else "suspended"
        return jsonify({'message': f'Link {status} successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ========== SUPER ADMIN: GET ALL PARTNER LINKS ==========
@referral_bp.route('/referral/admin/links', methods=['GET'])
@login_required
def admin_get_all_links():
    """Super admin only: View all referral links from all partners"""
    if current_user.role != 'super_admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        links = ReferralLink.query.order_by(ReferralLink.created_at.desc()).all()
        
        frontend_url = current_app.config.get('FRONTEND_URL', 'https://propeller-outclass-parsnip.ngrok-free.dev')
        
        return jsonify([{
            'id': l.id,
            'name': l.name,
            'link_code': l.link_code,
            'full_url': f"{frontend_url}/r/{l.link_code}",
            'destination_url': l.destination_url,
            'campaign_name': l.campaign_name,
            'is_active': l.is_active,
            'total_clicks': l.total_clicks,
            'unique_clicks': l.unique_clicks,
            'conversions': l.conversions,
            'created_at': l.created_at.isoformat(),
            'partner': {
                'id': l.user.id,
                'name': l.user.full_name,
                'email': l.user.email
            }
        } for l in links]), 200
        
    except Exception as e:
        print(f"Error fetching all links: {e}")
        return jsonify({'error': str(e)}), 500

# ========== SUPER ADMIN: CREATE LINK FOR PARTNER ==========
@referral_bp.route('/referral/admin/links', methods=['POST'])
@login_required
def admin_create_partner_link():
    """Super admin only: Create referral link for a specific partner"""
    if current_user.role != 'super_admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.json
        user_id = data.get('user_id')
        name = data.get('name', '').strip()
        destination_url = data.get('destination_url', '').strip()
        campaign_name = data.get('campaign_name', '').strip()
        
        # Validate
        if not user_id:
            return jsonify({'error': 'Partner user ID is required'}), 400
        if not name:
            return jsonify({'error': 'Link name is required'}), 400
        if not destination_url:
            return jsonify({'error': 'Destination URL is required'}), 400
        
        # Verify partner exists
        partner = User.query.get(user_id)
        if not partner:
            return jsonify({'error': 'Partner not found'}), 404
        
        # Generate unique code
        link_code = secrets.token_urlsafe(8)
        
        # Create link for partner
        link = ReferralLink(
            user_id=user_id,
            link_code=link_code,
            name=name,
            destination_url=destination_url,
            campaign_name=campaign_name,
            is_active=True,
            total_clicks=0,
            unique_clicks=0,
            conversions=0,
            created_at=datetime.utcnow()
        )
        
        db.session.add(link)
        db.session.commit()
        
        frontend_url = current_app.config.get('FRONTEND_URL', 'https://propeller-outclass-parsnip.ngrok-free.dev')
        
        return jsonify({
            'message': f'Referral link created for {partner.full_name}',
            'link': {
                'id': link.id,
                'name': link.name,
                'link_code': link.link_code,
                'full_url': f"{frontend_url}/r/{link.link_code}",
                'destination_url': link.destination_url,
                'campaign_name': link.campaign_name,
                'is_active': link.is_active,
                'partner': partner.full_name
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating partner link: {e}")
        return jsonify({'error': str(e)}), 500

# ========== SUPER ADMIN: GET PARTNER STATS ==========
@referral_bp.route('/referral/admin/partners', methods=['GET'])
@login_required
def admin_get_partner_stats():
    """Super admin only: Get referral stats for all partners"""
    if current_user.role != 'super_admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Get all users with referral links
        users = User.query.filter(User.referral_links.any()).all()
        
        stats = []
        for user in users:
            links = user.referral_links
            stats.append({
                'partner_id': user.id,
                'partner_name': user.full_name,
                'partner_email': user.email,
                'total_links': len(links),
                'active_links': sum(1 for l in links if l.is_active),
                'total_clicks': sum(l.total_clicks for l in links),
                'total_unique_clicks': sum(l.unique_clicks for l in links),
                'total_conversions': sum(l.conversions for l in links),
                'links': [{
                    'id': l.id,
                    'name': l.name,
                    'is_active': l.is_active,
                    'clicks': l.total_clicks
                } for l in links]
            })
        
        return jsonify(stats), 200
        
    except Exception as e:
        print(f"Error fetching partner stats: {e}")
        return jsonify({'error': str(e)}), 500




@referral_bp.route('/referral/analytics/partner', methods=['GET'])
@login_required
def get_partner_analytics():
    """Get analytics for the current partner - matches frontend expectations"""
    try:
        days = request.args.get('days', 30, type=int)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get all referral links for current user
        links = ReferralLink.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).all()
        
        link_ids = [l.id for l in links] if links else []
        
        # Get clicks within date range
        clicks = ReferralClick.query.filter(
            ReferralClick.link_id.in_(link_ids),
            ReferralClick.clicked_at >= start_date
        ).all() if link_ids else []
        
        # Calculate stats
        total_referrals = len(links)
        total_clicks = len(clicks)
        conversions = sum(1 for c in clicks if c.converted)
        pending = len([c for c in clicks if not c.converted])
        
        # Calculate conversion rate
        conversion_rate = round((conversions / total_clicks * 100), 2) if total_clicks > 0 else 0
        
        # Get recent referrals (last 5 clicks with details)
        recent_clicks = ReferralClick.query.filter(
            ReferralClick.link_id.in_(link_ids)
        ).order_by(ReferralClick.clicked_at.desc()).limit(5).all() if link_ids else []
        
        recent_referrals = []
        for click in recent_clicks:
            link = next((l for l in links if l.id == click.link_id), None)
            recent_referrals.append({
                'id': click.id,
                'link_name': link.name if link else 'Unknown',
                'ip_address': click.ip_address,
                'referrer_url': click.referrer_url or 'Direct',
                'converted': click.converted,
                'converted_at': click.clicked_at.isoformat() if click.converted else None,
                'clicked_at': click.clicked_at.isoformat() if click.clicked_at else None
            })
        
        # Get daily breakdown for chart
        daily_stats = {}
        for click in clicks:
            date_key = click.clicked_at.strftime('%Y-%m-%d')
            if date_key not in daily_stats:
                daily_stats[date_key] = {'clicks': 0, 'conversions': 0}
            daily_stats[date_key]['clicks'] += 1
            if click.converted:
                daily_stats[date_key]['conversions'] += 1
        
        # Generate full date range for chart
        chart_data = []
        current_date = start_date
        while current_date <= end_date:
            date_key = current_date.strftime('%Y-%m-%d')
            stats = daily_stats.get(date_key, {'clicks': 0, 'conversions': 0})
            chart_data.append({
                'date': date_key,
                'clicks': stats['clicks'],
                'conversions': stats['conversions']
            })
            current_date += timedelta(days=1)
        
        # Get top performing links
        top_links = sorted(links, key=lambda l: l.total_clicks, reverse=True)[:5]
        top_links_data = [{
            'id': l.id,
            'name': l.name,
            'link_code': l.link_code,
            'total_clicks': l.total_clicks,
            'unique_clicks': l.unique_clicks,
            'conversions': l.conversions,
            'conversion_rate': round((l.conversions / l.total_clicks * 100), 2) if l.total_clicks > 0 else 0
        } for l in top_links]
        
        # Return data matching frontend expectations
        return jsonify({
            'success': True,
            'data': {
                'total_referrals': total_referrals,
                'conversions': conversions,
                'pending': pending,
                'total_clicks': total_clicks,
                'conversion_rate': conversion_rate,
                'chart_data': chart_data,
                'recent_referrals': recent_referrals,
                'top_links': top_links_data,
                'period_days': days
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_partner_analytics: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    



@referral_bp.route('/referral/analytics/partner/summary', methods=['GET'])
@login_required
def get_partner_summary():
    """Get quick summary stats for partner dashboard"""
    try:
        # Get total links
        total_links = ReferralLink.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).count()
        
        # Get total clicks from user model
        total_clicks = current_user.total_clicks or 0
        total_conversions = current_user.total_conversions or 0
        
        # Get clicks from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_clicks = ReferralClick.query.join(
            ReferralLink
        ).filter(
            ReferralLink.user_id == current_user.id,
            ReferralClick.clicked_at >= thirty_days_ago
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_links': total_links,
                'total_clicks': total_clicks,
                'total_conversions': total_conversions,
                'recent_clicks': recent_clicks
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@referral_bp.route('/referral/track-nav', methods=['POST'])
def track_navigation():
    """Track navigation clicks from referral users"""
    try:
        data = request.json
        referral_code = data.get('referralCode')
        
        if not referral_code:
            return jsonify({'success': False, 'error': 'No referral code'}), 400
        
        # Get IP address
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')
        
        # Create navigation record
        from models import ReferralNavigation
        
        nav = ReferralNavigation(
            referral_code=referral_code,
            session_id=data.get('sessionId'),
            action=data.get('action', 'nav_click'),
            link_text=data.get('linkText', ''),
            link_href=data.get('linkHref', ''),
            link_id=data.get('linkId', ''),
            link_class=data.get('linkClass', ''),
            page_url=data.get('pageUrl', ''),
            page_title=data.get('pageTitle', ''),
            referrer_url=data.get('referrerUrl', ''),
            ip_address=ip_address,
            user_agent=user_agent[:500],  # Limit length
            screen_size=data.get('screenSize', ''),
            time_spent=data.get('timeSpent', 0)
        )
        
        db.session.add(nav)
        db.session.commit()
        
        print(f"📊 Referral Navigation: {referral_code} -> {data.get('linkText', 'Unknown')}")
        
        return jsonify({
            'success': True,
            'message': 'Navigation tracked'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error tracking navigation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@referral_bp.route('/referral/analytics/navigation', methods=['GET'])
@login_required
def get_navigation_analytics():
    """Get navigation analytics for a partner"""
    try:
        referral_code = request.args.get('code')
        days = request.args.get('days', 30, type=int)
        
        from models import ReferralNavigation, ReferralLink
        
        # If no code provided, get the partner's referral code
        if not referral_code:
            link = ReferralLink.query.filter_by(
                user_id=current_user.id,
                is_active=True
            ).first()
            if link:
                referral_code = link.link_code
        
        if not referral_code:
            return jsonify({'error': 'No referral code found'}), 404
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get navigation data
        navigations = ReferralNavigation.query.filter(
            ReferralNavigation.referral_code == referral_code,
            ReferralNavigation.created_at >= start_date
        ).order_by(ReferralNavigation.created_at.desc()).all()
        
        # Aggregated stats
        total_clicks = ReferralNavigation.query.filter_by(
            referral_code=referral_code,
            action='nav_click'
        ).count()
        
        total_exits = ReferralNavigation.query.filter_by(
            referral_code=referral_code,
            action='exit'
        ).count()
        
        # Most visited pages
        page_stats = db.session.query(
            ReferralNavigation.page_url,
            func.count(ReferralNavigation.id).label('visits')
        ).filter(
            ReferralNavigation.referral_code == referral_code,
            ReferralNavigation.page_url != ''
        ).group_by(
            ReferralNavigation.page_url
        ).order_by(
            func.count(ReferralNavigation.id).desc()
        ).limit(10).all()
        
        # Most clicked links
        link_stats = db.session.query(
            ReferralNavigation.link_text,
            ReferralNavigation.link_href,
            func.count(ReferralNavigation.id).label('clicks')
        ).filter(
            ReferralNavigation.referral_code == referral_code,
            ReferralNavigation.link_text != ''
        ).group_by(
            ReferralNavigation.link_text,
            ReferralNavigation.link_href
        ).order_by(
            func.count(ReferralNavigation.id).desc()
        ).limit(10).all()
        
        # Average time on page
        avg_time = db.session.query(
            func.avg(ReferralNavigation.time_spent)
        ).filter(
            ReferralNavigation.referral_code == referral_code,
            ReferralNavigation.action == 'exit',
            ReferralNavigation.time_spent > 0
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'data': {
                'summary': {
                    'total_navigations': len(navigations),
                    'total_clicks': total_clicks,
                    'total_exits': total_exits,
                    'avg_time_on_page': round(avg_time, 1),
                    'period_days': days
                },
                'top_pages': [{
                    'url': p.page_url,
                    'visits': p.visits
                } for p in page_stats],
                'top_links': [{
                    'text': l.link_text,
                    'href': l.link_href,
                    'clicks': l.clicks
                } for l in link_stats],
                'recent_activity': [n.to_dict() for n in navigations[:50]]
            }
        }), 200
        
    except Exception as e:
        print(f"Error getting navigation analytics: {e}")
        return jsonify({'error': str(e)}), 500