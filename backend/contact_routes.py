# backend/contact_routes.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, ContactMessage
from datetime import datetime
import re
from email_service import EmailService




contact_bp = Blueprint('contact', __name__)
email_service = EmailService()


def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ========== PUBLIC CONTACT FORM ==========
@contact_bp.route('/contact', methods=['POST'])
def submit_contact():
    """Submit a contact message (public)"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        email = data.get('email', '').lower().strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        
        print(f"Contact form submission: {name}, {email}, {subject}")
        
        # Validate required fields
        if not all([name, email, subject, message]):
            return jsonify({'error': 'All fields are required'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email address'}), 400
        
        if len(message) < 10:
            return jsonify({'error': 'Message must be at least 10 characters'}), 400
        
        # Create contact message
        contact = ContactMessage(
            name=name,
            email=email,
            subject=subject,
            message=message,
            status='unread',
            created_at=datetime.utcnow()
        )
        
        db.session.add(contact)
        db.session.commit()
        
        print(f"Contact message saved with ID: {contact.id}")
        
        return jsonify({
            'message': 'Thank you for your message! We will get back to you soon.',
            'id': contact.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in submit_contact: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to send message'}), 500


# ========== ADMIN CONTACT MANAGEMENT ==========
@contact_bp.route('/admin/contacts', methods=['GET'])
@login_required
def get_contacts():
    """Get all contact messages (admin only)"""
    try:
        # Check if user is admin or super admin
        if not current_user.is_super_admin() and not current_user.is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Optional: Filter by status
        status = request.args.get('status', None)
        query = ContactMessage.query.order_by(ContactMessage.created_at.desc())
        
        if status:
            query = query.filter_by(status=status)
        
        contacts = query.all()
        return jsonify([c.to_dict() for c in contacts]), 200
        
    except Exception as e:
        print(f"Error in get_contacts: {e}")
        return jsonify([]), 200


@contact_bp.route('/admin/contacts/stats', methods=['GET'])
@login_required
def get_contact_stats():
    """Get contact statistics (admin only)"""
    try:
        if not current_user.is_super_admin() and not current_user.is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        total = ContactMessage.query.count()
        unread = ContactMessage.query.filter_by(status='unread').count()
        read = ContactMessage.query.filter_by(status='read').count()
        replied = ContactMessage.query.filter_by(status='replied').count()
        archived = ContactMessage.query.filter_by(status='archived').count()
        
        return jsonify({
            'total': total,
            'unread': unread,
            'read': read,
            'replied': replied,
            'archived': archived
        }), 200
        
    except Exception as e:
        print(f"Error in get_contact_stats: {e}")
        return jsonify({'total': 0, 'unread': 0, 'read': 0, 'replied': 0, 'archived': 0}), 200


@contact_bp.route('/admin/contacts/<int:id>', methods=['GET'])
@login_required
def get_contact(id):
    """Get single contact message (admin only)"""
    try:
        if not current_user.is_super_admin() and not current_user.is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        contact = ContactMessage.query.get_or_404(id)
        
        # Mark as read if it was unread
        if contact.status == 'unread':
            contact.status = 'read'
            db.session.commit()
        
        return jsonify(contact.to_dict()), 200
        
    except Exception as e:
        print(f"Error in get_contact: {e}")
        return jsonify({'error': 'Contact not found'}), 404


@contact_bp.route('/admin/contacts/<int:id>/status', methods=['PUT'])
@login_required
def update_contact_status(id):
    """Update contact message status (admin only)"""
    try:
        if not current_user.is_super_admin() and not current_user.is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        contact = ContactMessage.query.get_or_404(id)
        data = request.json
        new_status = data.get('status')
        
        if new_status not in ['unread', 'read', 'replied', 'archived']:
            return jsonify({'error': 'Invalid status'}), 400
        
        contact.status = new_status
        db.session.commit()
        
        return jsonify({'message': f'Status updated to {new_status}'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_contact_status: {e}")
        return jsonify({'error': str(e)}), 500

@contact_bp.route('/admin/contacts/<int:id>/reply', methods=['POST'])
@login_required
def reply_contact(id):
    """Reply to a contact message (admin only)"""
    try:
        if not current_user.is_super_admin() and not current_user.is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        contact = ContactMessage.query.get_or_404(id)
        data = request.json
        reply_message = data.get('reply_message', '').strip()
        
        if not reply_message:
            return jsonify({'error': 'Reply message is required'}), 400
        
        # Send email reply
        email_sent = email_service.send_contact_reply(
            contact_name=contact.name,
            contact_email=contact.email,
            subject=contact.subject,
            reply_message=reply_message
        )
        
        if email_sent:
            # Update contact status
            contact.status = 'replied'
            contact.replied_by = current_user.id
            contact.replied_at = datetime.utcnow()
            db.session.commit()
            
            print(f"\n{'='*50}")
            print(f"📧 Reply sent to {contact.email}")
            print(f"Subject: Re: {contact.subject}")
            print(f"{'='*50}\n")
            
            return jsonify({'message': 'Reply sent successfully via email'}), 200
        else:
            return jsonify({'error': 'Failed to send email. Please check SMTP settings.'}), 500
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in reply_contact: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@contact_bp.route('/admin/contacts/<int:id>', methods=['DELETE'])
@login_required
def delete_contact(id):
    """Delete a contact message (super admin only)"""
    try:
        if not current_user.is_super_admin():
            return jsonify({'error': 'Unauthorized - Super admin only'}), 403
        
        contact = ContactMessage.query.get_or_404(id)
        db.session.delete(contact)
        db.session.commit()
        
        return jsonify({'message': 'Contact deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_contact: {e}")
        return jsonify({'error': str(e)}), 500