# backend/newsletter_routes.py
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from permission_service import has_permission
from models import db, NewsletterSubscriber, User, ActivityLog
from datetime import datetime
import secrets
import re
from email_service import email_service

newsletter_bp = Blueprint('newsletter', __name__)

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def log_activity(user_id, user_name, action, resource_type, resource_id, description):
    """Log user activity"""
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

# ========== PUBLIC ROUTES ==========

@newsletter_bp.route('/newsletter/subscribe', methods=['POST'])
def subscribe():
    """Public endpoint for newsletter subscription"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not is_valid_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if already subscribed
        existing = NewsletterSubscriber.query.filter_by(email=email).first()
        
        if existing:
            if existing.is_active:
                return jsonify({'message': 'Email already subscribed'}), 200
            else:
                # Reactivate
                existing.is_active = True
                existing.subscribed_at = datetime.utcnow()
                db.session.commit()
                return jsonify({'message': 'Subscription reactivated'}), 200
        
        # Create new subscriber
        subscriber = NewsletterSubscriber(
            name=name,
            email=email,
            subscribed_at=datetime.utcnow(),
            is_active=True
        )
        db.session.add(subscriber)
        db.session.commit()
        
        # Send welcome email
        try:
            frontend_url = current_app.config.get('FRONTEND_URL', 'https://propeller-outclass-parsnip.ngrok-free.dev')
            unsubscribe_token = secrets.token_urlsafe(32)
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Welcome to Meru Dairy Newsletter</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ padding: 30px; background: #f9fafb; }}
                    .button {{ display: inline-block; padding: 12px 30px; background: #f59e0b; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #ddd; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Welcome to Meru Dairy Newsletter!</h2>
                    </div>
                    <div class="content">
                        <p>Dear <strong>{name or 'Valued Customer'}</strong>,</p>
                        <p>Thank you for subscribing to the Meru Dairy newsletter!</p>
                        <p>You'll receive updates about:</p>
                        <ul>
                            <li>New product launches</li>
                            <li>Special promotions and offers</li>
                            <li>Dairy industry news</li>
                            <li>Farmer success stories</li>
                        </ul>
                        <p>We're excited to have you as part of our community!</p>
                        <p>Best regards,<br>
                        <strong>Meru Central Dairy Team</strong></p>
                    </div>
                    <div class="footer">
                        <p>Meru Central Dairy Co-operative Union Ltd</p>
                        <p><a href="{frontend_url}/unsubscribe?email={email}&token={unsubscribe_token}" style="color: #666;">Unsubscribe</a> at any time.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            email_service._send_email(email, "Welcome to Meru Dairy Newsletter", html)
        except Exception as e:
            print(f"Error sending welcome email: {e}")
        
        return jsonify({'message': 'Subscribed successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in subscribe: {e}")
        return jsonify({'error': str(e)}), 500

@newsletter_bp.route('/newsletter/unsubscribe', methods=['POST'])
def unsubscribe():
    """Public endpoint to unsubscribe"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        subscriber = NewsletterSubscriber.query.filter_by(email=email).first()
        
        if subscriber:
            subscriber.is_active = False
            db.session.commit()
            return jsonify({'message': 'Unsubscribed successfully'}), 200
        
        return jsonify({'message': 'Email not found'}), 404
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in unsubscribe: {e}")
        return jsonify({'error': str(e)}), 500

# ========== ADMIN ROUTES ==========

@newsletter_bp.route('/admin/newsletter/subscribers', methods=['GET'])
@login_required
def get_subscribers():
    """Get all newsletter subscribers - Admin only"""
    if not has_permission(current_user, 'newsletter', 'read'):
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status', 'all')
        
        query = NewsletterSubscriber.query
        
        if search:
            query = query.filter(
                db.or_(
                    NewsletterSubscriber.email.ilike(f'%{search}%'),
                    NewsletterSubscriber.name.ilike(f'%{search}%')
                )
            )
        
        if status == 'active':
            query = query.filter_by(is_active=True)
        elif status == 'inactive':
            query = query.filter_by(is_active=False)
        
        paginated = query.order_by(NewsletterSubscriber.subscribed_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'data': [{
                'id': s.id,
                'name': s.name,
                'email': s.email,
                'is_active': s.is_active,
                'subscribed_at': s.subscribed_at.isoformat() if s.subscribed_at else None,
                'last_sent': s.last_sent.isoformat() if s.last_sent else None
            } for s in paginated.items],
            'pagination': {
                'current_page': paginated.page,
                'total_pages': paginated.pages,
                'total_items': paginated.total,
                'has_next': paginated.has_next,
                'has_prev': paginated.has_prev
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_subscribers: {e}")
        return jsonify([]), 500

@newsletter_bp.route('/admin/newsletter/subscribers/stats', methods=['GET'])
@login_required
def get_subscriber_stats():
    """Get newsletter statistics - Admin only"""
    if not has_permission(current_user, 'newsletter', 'read'):
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        total = NewsletterSubscriber.query.count()
        active = NewsletterSubscriber.query.filter_by(is_active=True).count()
        inactive = NewsletterSubscriber.query.filter_by(is_active=False).count()
        
        # Get new subscribers in last 30 days
        thirty_days_ago = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        from datetime import timedelta
        thirty_days_ago = thirty_days_ago - timedelta(days=30)
        new_last_30 = NewsletterSubscriber.query.filter(
            NewsletterSubscriber.subscribed_at >= thirty_days_ago
        ).count()
        
        return jsonify({
            'total': total,
            'active': active,
            'inactive': inactive,
            'new_last_30_days': new_last_30
        }), 200
        
    except Exception as e:
        print(f"Error in get_subscriber_stats: {e}")
        return jsonify({'error': str(e)}), 500

@newsletter_bp.route('/admin/newsletter/subscribers/<int:subscriber_id>', methods=['DELETE'])
@login_required
def delete_subscriber(subscriber_id):
    """Delete a subscriber - Super Admin only"""
    if not has_permission(current_user, 'newsletter', 'delete'):
        return jsonify({'error': 'Super admin access required'}), 403
    
    try:
        subscriber = NewsletterSubscriber.query.get_or_404(subscriber_id)
        db.session.delete(subscriber)
        db.session.commit()
        
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='delete',
            resource_type='newsletter',
            resource_id=subscriber_id,
            description=f'Deleted newsletter subscriber: {subscriber.email}'
        )
        
        return jsonify({'message': 'Subscriber deleted'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_subscriber: {e}")
        return jsonify({'error': str(e)}), 500

@newsletter_bp.route('/admin/newsletter/subscribers/<int:subscriber_id>/toggle', methods=['PUT'])
@login_required
def toggle_subscriber_status(subscriber_id):
    """Toggle subscriber active status - Admin only"""
    if not has_permission(current_user, 'newsletter', 'update'):
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        subscriber = NewsletterSubscriber.query.get_or_404(subscriber_id)
        subscriber.is_active = not subscriber.is_active
        db.session.commit()
        
        status = 'activated' if subscriber.is_active else 'deactivated'
        
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='toggle',
            resource_type='newsletter',
            resource_id=subscriber_id,
            description=f'{status} newsletter subscriber: {subscriber.email}'
        )
        
        return jsonify({'message': f'Subscriber {status}'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in toggle_subscriber_status: {e}")
        return jsonify({'error': str(e)}), 500

@newsletter_bp.route('/admin/newsletter/send', methods=['POST'])
@login_required
def send_newsletter():
    """Send newsletter to all active subscribers - Admin only"""
    if not has_permission(current_user, 'newsletter', 'create'):
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        data = request.json
        subject = data.get('subject', '').strip()
        content = data.get('content', '').strip()
        is_test = data.get('is_test', False)
        test_email = data.get('test_email', '')
        
        if not subject or not content:
            return jsonify({'error': 'Subject and content are required'}), 400
        
        if is_test and not test_email:
            return jsonify({'error': 'Test email address required'}), 400
        
        frontend_url = current_app.config.get('FRONTEND_URL', 'https://propeller-outclass-parsnip.ngrok-free.dev')
        
        if is_test:
            # Send test email
            unsubscribe_token = secrets.token_urlsafe(32)
            html = build_newsletter_html(subject, content, test_email, unsubscribe_token, frontend_url)
            email_service._send_email(test_email, f"[TEST] {subject}", html)
            return jsonify({'message': 'Test email sent'}), 200
        
        # Get all active subscribers
        subscribers = NewsletterSubscriber.query.filter_by(is_active=True).all()
        
        if not subscribers:
            return jsonify({'error': 'No active subscribers'}), 400
        
        sent_count = 0
        failed_count = 0
        
        for subscriber in subscribers:
            try:
                unsubscribe_token = secrets.token_urlsafe(32)
                html = build_newsletter_html(subject, content, subscriber.email, unsubscribe_token, frontend_url)
                
                if email_service._send_email(subscriber.email, subject, html):
                    sent_count += 1
                    subscriber.last_sent = datetime.utcnow()
                else:
                    failed_count += 1
            except Exception as e:
                print(f"Error sending to {subscriber.email}: {e}")
                failed_count += 1
        
        db.session.commit()
        
        log_activity(
            user_id=current_user.id,
            user_name=current_user.full_name,
            action='send_newsletter',
            resource_type='newsletter',
            resource_id=0,
            description=f'Sent newsletter "{subject}" to {sent_count} subscribers'
        )
        
        return jsonify({
            'message': f'Newsletter sent to {sent_count} subscribers',
            'sent': sent_count,
            'failed': failed_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in send_newsletter: {e}")
        return jsonify({'error': str(e)}), 500

def build_newsletter_html(subject, content, email, unsubscribe_token, frontend_url):
    """Build HTML for newsletter email"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{subject}</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 30px; text-align: center; }}
            .content {{ padding: 30px; background: #f9fafb; }}
            .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #ddd; }}
            .unsubscribe {{ color: #f59e0b; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Meru Dairy Newsletter</h2>
            </div>
            <div class="content">
                <h3>{subject}</h3>
                <div style="white-space: pre-wrap;">{content}</div>
            </div>
            <div class="footer">
                <p>Meru Central Dairy Co-operative Union Ltd</p>
                <p><a href="{frontend_url}/unsubscribe?email={email}&token={unsubscribe_token}" class="unsubscribe">Unsubscribe</a> from future emails</p>
            </div>
        </div>
    </body>
    </html>
    """

@newsletter_bp.route('/admin/newsletter/export', methods=['GET'])
@login_required
def export_subscribers():
    """Export subscribers to CSV - Admin only"""
    if not has_permission(current_user, 'newsletter', 'read'):
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        import csv
        from io import StringIO
        
        subscribers = NewsletterSubscriber.query.filter_by(is_active=True).order_by(NewsletterSubscriber.subscribed_at.desc()).all()
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Name', 'Email', 'Subscribed Date', 'Status'])
        
        for sub in subscribers:
            writer.writerow([
                sub.name or '',
                sub.email,
                sub.subscribed_at.strftime('%Y-%m-%d %H:%M:%S') if sub.subscribed_at else '',
                'Active' if sub.is_active else 'Inactive'
            ])
        
        response = jsonify({
            'csv_content': output.getvalue(),
            'filename': f'newsletter_subscribers_{datetime.utcnow().strftime("%Y%m%d")}.csv'
        })
        return response, 200
        
    except Exception as e:
        print(f"Error in export_subscribers: {e}")
        return jsonify({'error': str(e)}), 500