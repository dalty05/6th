from flask import Blueprint, request, jsonify, current_app, send_file
from flask_login import login_required, current_user
from models import db, TourPackage, TourBooking, TourAvailability, TourPayment, TourInvoice, User
from datetime import datetime, timedelta
import json
import os
from sqlalchemy import func, and_, or_

from services.tour_email_service import TourEmailService



 
# REPORTLAB PDF export

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ ReportLab not available. PDF export disabled.")



tour_bp = Blueprint('tour', __name__)


# PUBLIC ROUTES (No Authentication Required)


@tour_bp.route('/tour/packages', methods=['GET'])
def get_packages():
    """Get all active tour packages"""
    try:
        packages = TourPackage.query.filter_by(is_active=True).all()
        return jsonify({
            'packages': [pkg.to_dict() for pkg in packages]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tour_bp.route('/tour/availability', methods=['GET'])
def check_availability():
    """Check if a date is available for booking"""
    try:
        package_id = request.args.get('package_id', type=int)
        date_str = request.args.get('date')
        
        if not package_id or not date_str:
            return jsonify({'error': 'Package ID and date are required'}), 400
        
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # ✅ Check if date is blocked
        availability = TourAvailability.query.filter_by(
            package_id=package_id,
            date=target_date
        ).first()
        
        if availability:
            return jsonify({
                'date': date_str,
                'is_blocked': availability.is_blocked,
                'block_reason': availability.block_reason,
                'is_available': not availability.is_blocked
            }), 200
        else:
            # ✅ No availability record = available
            return jsonify({
                'date': date_str,
                'is_blocked': False,
                'block_reason': None,
                'is_available': True
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tour_bp.route('/tour/booking', methods=['POST'])
def create_booking():
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        print(f"📥 Booking request data: {data}")
        
        # Validate required fields
        required_fields = ['package_id', 'tour_date', 'people_count', 
                          'customer_name', 'customer_email', 'customer_phone']
        
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Get package
        package = TourPackage.query.get(data['package_id'])
        if not package or not package.is_active:
            return jsonify({'error': 'Invalid or inactive package'}), 400
        
        people_count = int(data['people_count'])
        
        # ✅ Check package min/max limits
        if people_count < package.min_people:
            return jsonify({'error': f'Minimum {package.min_people} people required'}), 400
        
        if people_count > package.max_people:
            return jsonify({
                'error': f'Maximum {package.max_people} people allowed for this tour'
            }), 400
        
        tour_date = datetime.strptime(data['tour_date'], '%Y-%m-%d %H:%M:%S')
        
        # ✅ Check if date is blocked (optional - remove if you want no blocking)
        availability = TourAvailability.query.filter_by(
            package_id=package.id,
            date=tour_date.date()
        ).first()
        
        if availability and availability.is_blocked:
            return jsonify({'error': 'This date is not available'}), 400
        
        # ✅ Create booking - ALWAYS PENDING
        booking = TourBooking(
            package_id=package.id,
            tour_date=tour_date,
            people_count=people_count,
            customer_name=data['customer_name'].strip(),
            customer_email=data['customer_email'].strip(),
            customer_phone=data['customer_phone'].strip(),
            special_requirements=data.get('special_requirements'),
            group_name=data.get('group_name'),
            status='pending',  # ✅ ALL bookings start as pending
            payment_status='pending'
        )
        
        booking.generate_reference()
        
        # Calculate price
        price_data = package.get_price_for_people(people_count)
        
        booking.price_per_person = price_data['base_price']
        booking.subtotal = price_data['subtotal']
        booking.discount_applied = price_data['discount_amount']
        booking.total_amount = price_data['total']
        
        # Use package commitment percentage
        commitment_percentage = package.commitment_percentage or 30.0
        booking.commitment_amount = price_data['total'] * (commitment_percentage / 100)
        
        db.session.add(booking)
        db.session.commit()
        
        print(f"✅ Booking created: {booking.reference} (Status: pending)")
        
        # ✅ Send booking received email
        try:
            from services.tour_email_service import TourEmailService
            email_service = TourEmailService()
            email_service.send_booking_received(booking)
        except Exception as e:
            print(f"❌ Failed to send booking received email: {e}")
        except Exception as e:
            print(f"Email error: {e}")
        
        price_data['commitment_deposit'] = booking.commitment_amount
        price_data['remaining_balance'] = price_data['total'] - booking.commitment_amount
        price_data['status'] = 'pending'
        price_data['requires_approval'] = True
        
        return jsonify({
            'success': True,
            'message': 'Booking submitted for approval. Our team will review and confirm within 24 hours.',
            'booking': booking.to_dict(include_package=True),
            'price_breakdown': price_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Booking error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



# ADMIN ROUTES 




@tour_bp.route('/tour/admin/bookings', methods=['GET'])
@login_required
def get_all_bookings():
    """Get all bookings with filters"""
    try:
        status = request.args.get('status')
        package_id = request.args.get('package_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        per_page = request.args.get('per_page', type=int, default=20)
        page = request.args.get('page', type=int, default=1)
        
        query = TourBooking.query
        
        if status:
            query = query.filter_by(status=status)
        if package_id:
            query = query.filter_by(package_id=package_id)
        if date_from:
            query = query.filter(TourBooking.tour_date >= datetime.strptime(date_from, '%Y-%m-%d'))
        if date_to:
            query = query.filter(TourBooking.tour_date <= datetime.strptime(date_to, '%Y-%m-%d'))
        
        query = query.order_by(TourBooking.created_at.desc())
        
        total = query.count()
        bookings = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return jsonify({
            'bookings': [b.to_dict(include_package=True) for b in bookings],
            'count': len(bookings),
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        print(f"❌ Error in get_all_bookings: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@tour_bp.route('/tour/admin/bookings/<int:booking_id>', methods=['GET'])
@login_required
def get_booking(booking_id):
    """Get a single booking by ID"""
    try:
        booking = TourBooking.query.get_or_404(booking_id)
        return jsonify(booking.to_dict(include_package=True)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tour_bp.route('/tour/admin/bookings/<int:booking_id>/status', methods=['PUT'])
@login_required
def update_booking_status(booking_id):
    try:
        booking = TourBooking.query.get_or_404(booking_id)
        data = request.get_json()
        
        new_status = data.get('status')
        notes = data.get('notes')
        
        valid_statuses = ['pending', 'confirmed', 'rejected', 'completed', 'cancelled', 'commitment_pending', 'cleared']
        if new_status not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400
        
        old_status = booking.status
        booking.status = new_status
        if notes:
            booking.notes = notes
        booking.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # ✅ Send email notifications based on status change
        try:
            email_service = TourEmailService()
            if new_status == 'confirmed' and old_status != 'confirmed':
                email_service.send_booking_confirmed(booking)
            elif new_status == 'rejected' and old_status != 'rejected':
                email_service.send_booking_rejected(booking, notes or 'No reason provided')
            elif new_status == 'cancelled' and old_status != 'cancelled':
                email_service.send_booking_cancelled(booking, notes or 'Cancelled by manager')
        except Exception as e:
            print(f"❌ Failed to send status update email: {e}")
        
        return jsonify({
            'success': True,
            'message': f'Booking {new_status} successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@tour_bp.route('/tour/admin/bookings/<int:booking_id>/change-request', methods=['POST'])
@login_required
def handle_change_request(booking_id):
    """Handle date change request"""
    try:
        booking = TourBooking.query.get_or_404(booking_id)
        data = request.get_json()
        
        action = data.get('action')
        
        if action == 'approve':
            booking.approve_date_change()
            message = 'Date change approved'
        elif action == 'reject':
            booking.reject_date_change()
            message = 'Date change rejected'
        else:
            return jsonify({'error': 'Invalid action'}), 400
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@tour_bp.route('/tour/admin/bookings/<int:booking_id>/payment', methods=['PUT'])
@login_required
def confirm_payment(booking_id):
    try:
        booking = TourBooking.query.get_or_404(booking_id)
        data = request.get_json()
        
        payment_amount = data.get('amount')
        payment_type = data.get('payment_type')
        payment_method = data.get('payment_method', 'manual')
        reference_number = data.get('reference_number')
        notes = data.get('notes')
        
        if not payment_amount or not payment_type:
            return jsonify({'error': 'Amount and payment type are required'}), 400
        
        # ✅ Check if booking can accept payments
        if booking.status in ['rejected', 'cancelled']:
            return jsonify({
                'error': f'Cannot process payment for a {booking.status} booking'
            }), 400
        
        # ✅ Check if booking is already fully paid
        if booking.payment_status == 'fully_paid':
            return jsonify({
                'error': 'This booking is already fully paid'
            }), 400
        
        # Update booking payment status
        if payment_type == 'commitment':
            # ✅ Check if commitment already paid
            if booking.commitment_paid:
                return jsonify({
                    'error': 'Commitment deposit has already been paid'
                }), 400
            
            booking.commitment_paid = True
            booking.commitment_paid_date = datetime.utcnow()
            booking.payment_status = 'commitment_paid'
            if booking.status == 'confirmed':
                booking.status = 'commitment_pending'
                
        elif payment_type == 'balance' or payment_type == 'full':
            # ✅ Check if already fully paid
            if booking.payment_status == 'fully_paid':
                return jsonify({
                    'error': 'This booking is already fully paid'
                }), 400
            
            booking.full_payment_date = datetime.utcnow()
            booking.payment_status = 'fully_paid'
            booking.status = 'cleared'
            
        else:
            return jsonify({'error': 'Invalid payment type'}), 400
        
        # Create payment record
        payment = TourPayment(
            booking_id=booking.id,
            amount=payment_amount,
            payment_type=payment_type,
            payment_method=payment_method,
            reference_number=reference_number,
            verification_notes=notes,
            verified_by_id=current_user.id,
            verification_date=datetime.utcnow(),
            status='verified'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # Send payment received email
        try:
            from services.tour_email_service import TourEmailService
            email_service = TourEmailService()
            email_service.send_payment_received(booking, payment_amount, payment_type)
        except Exception as e:
            print(f"Email error: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Payment confirmed successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Payment error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@tour_bp.route('/tour/admin/bookings/<int:booking_id>/certificate', methods=['GET'])
@login_required
def download_certificate(booking_id):
    """Download clearance certificate PDF"""
    try:
        booking = TourBooking.query.get_or_404(booking_id)
        
        if not current_user.is_super_admin() and not current_user.is_admin() and not current_user.is_tour_manager():
            if current_user.id != booking.customer_user_id:
                return jsonify({'error': 'Permission denied'}), 403
        
        if booking.status not in ['cleared', 'completed']:
            return jsonify({'error': 'Certificate only available for cleared bookings'}), 400
        
        try:
            from services.tour_pdf_service import TourPDFService
            pdf_service = TourPDFService()
            filepath, filename = pdf_service.generate_certificate(booking)
            
            return send_file(
                filepath,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )
        except ImportError:
            return jsonify({'error': 'PDF service not available'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tour_bp.route('/tour/admin/packages', methods=['GET'])
@login_required
def get_admin_packages():
    """Get all packages for admin"""
    try:
        packages = TourPackage.query.all()
        return jsonify({
            'packages': [pkg.to_dict() for pkg in packages]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tour_bp.route('/tour/admin/packages', methods=['POST'])
@login_required
def create_package():
    """Create a new tour package"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'slug', 'description', 'base_price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        package = TourPackage(
            name=data['name'],
            slug=data['slug'],
            description=data['description'],
            short_description=data.get('short_description'),
            base_price=data['base_price'],
            min_people=data.get('min_people', 1),
            max_people=data.get('max_people', 300),
            commitment_percentage=data.get('commitment_percentage', 30.0),
            discount_tiers=data.get('discount_tiers', {
                '1-50': 0.05,
                '51-100': 0.10,
                '101-150': 0.15,
                '151-200': 0.20,
                '201+': 0.25
            }),
            duration_hours=data.get('duration_hours', 2),
            includes=data.get('includes', []),
            excludes=data.get('excludes', []),
            image_url=data.get('image_url'),
            gallery_images=data.get('gallery_images', []),
            is_active=data.get('is_active', True),
            is_featured=data.get('is_featured', False),
            created_by_id=current_user.id
        )
        
        db.session.add(package)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Package created successfully',
            'package': package.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tour_bp.route('/tour/admin/packages/<int:package_id>', methods=['PUT'])
@login_required
def update_package(package_id):
    """Update a tour package"""
    try:
        package = TourPackage.query.get_or_404(package_id)
        data = request.get_json()
        
        if 'name' in data:
            package.name = data['name']
        if 'slug' in data:
            package.slug = data['slug']
        if 'description' in data:
            package.description = data['description']
        if 'short_description' in data:
            package.short_description = data['short_description']
        if 'base_price' in data:
            package.base_price = data['base_price']
        if 'min_people' in data:
            package.min_people = data['min_people']
        if 'max_people' in data:
            package.max_people = data['max_people']
        if 'discount_tiers' in data:
            package.discount_tiers = data['discount_tiers']
        if 'commitment_percentage' in data:  # ✅ Add this
            package.commitment_percentage = data['commitment_percentage']

        if 'duration_hours' in data:
            package.duration_hours = data['duration_hours']
        if 'includes' in data:
            package.includes = data['includes']
        if 'excludes' in data:
            package.excludes = data['excludes']
        if 'image_url' in data:
            package.image_url = data['image_url']
        if 'gallery_images' in data:
            package.gallery_images = data['gallery_images']
        if 'is_active' in data:
            package.is_active = data['is_active']
        if 'is_featured' in data:
            package.is_featured = data['is_featured']
        
        package.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Package updated successfully',
            'package': package.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tour_bp.route('/tour/admin/packages/<int:package_id>', methods=['DELETE'])
@login_required
def delete_package(package_id):
    """Delete a tour package"""
    try:
        package = TourPackage.query.get_or_404(package_id)
        
        if package.bookings.count() > 0:
            return jsonify({'error': 'Cannot delete package with existing bookings'}), 400
        
        db.session.delete(package)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Package deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tour_bp.route('/tour/admin/availability', methods=['PUT'])
@login_required
def update_availability():
    """Update availability for a specific date"""
    try:
        data = request.get_json()
        
        package_id = data.get('package_id')
        date_str = data.get('date')
        capacity = data.get('capacity')
        is_blocked = data.get('is_blocked', False)
        block_reason = data.get('block_reason')
        
        if not package_id or not date_str:
            return jsonify({'error': 'Package ID and date are required'}), 400
        
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        availability = TourAvailability.query.filter_by(
            package_id=package_id,
            date=target_date
        ).first()
        
        if not availability:
            availability = TourAvailability(
                package_id=package_id,
                date=target_date,
                capacity=capacity or 500,
                booked=0
            )
            db.session.add(availability)
        else:
            if capacity is not None:
                availability.capacity = capacity
            availability.is_blocked = is_blocked
            if block_reason is not None:
                availability.block_reason = block_reason
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Availability updated successfully',
            'availability': availability.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tour_bp.route('/tour/admin/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        total_bookings = TourBooking.query.count()
        pending_bookings = TourBooking.query.filter_by(status='pending').count()
        confirmed_bookings = TourBooking.query.filter_by(status='confirmed').count()
        completed_bookings = TourBooking.query.filter_by(status='completed').count()
        commitment_pending = TourBooking.query.filter_by(status='commitment_pending').count()
        cleared_bookings = TourBooking.query.filter_by(status='cleared').count()
        
        completed_tours = TourBooking.query.filter_by(status='completed').all()
        total_revenue = sum(tour.total_amount for tour in completed_tours)
        
        upcoming = TourBooking.query.filter(
            TourBooking.tour_date >= datetime.utcnow(),
            TourBooking.tour_date <= datetime.utcnow() + timedelta(days=7),
            TourBooking.status.in_(['confirmed', 'commitment_pending', 'cleared'])
        ).count()
        
        return jsonify({
            'total_bookings': total_bookings,
            'pending_bookings': pending_bookings,
            'confirmed_bookings': confirmed_bookings,
            'completed_bookings': completed_bookings,
            'commitment_pending': commitment_pending,
            'cleared_bookings': cleared_bookings,
            'upcoming_tours': upcoming,
            'total_revenue': total_revenue
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

 
# REPORTING ROUTES
 

@tour_bp.route('/tour/admin/reports/summary', methods=['GET'])
@login_required
def get_report_summary():
    """Get report summary for date range"""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if not start_date_str or not end_date_str:
            return jsonify({'error': 'Start date and end date are required'}), 400
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
        
        bookings = TourBooking.query.filter(
            TourBooking.created_at >= start_date,
            TourBooking.created_at < end_date
        ).all()
        
        total_bookings = len(bookings)
        total_revenue = sum(b.total_amount for b in bookings if b.status == 'completed')
        total_visitors = sum(b.people_count for b in bookings)
        
        completed = len([b for b in bookings if b.status == 'completed'])
        conversion_rate = round((completed / total_bookings * 100), 1) if total_bookings > 0 else 0
        
        package_counts = {}
        for b in bookings:
            if b.package_id:
                package_counts[b.package_id] = package_counts.get(b.package_id, 0) + 1
        
        popular_packages = []
        for pkg_id, count in sorted(package_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            pkg = TourPackage.query.get(pkg_id)
            if pkg:
                popular_packages.append({
                    'id': pkg.id,
                    'name': pkg.name,
                    'total_bookings': count,
                    'percentage': round((count / total_bookings * 100), 1) if total_bookings > 0 else 0
                })
        
        recent = TourBooking.query.filter(
            TourBooking.created_at >= start_date,
            TourBooking.created_at < end_date
        ).order_by(TourBooking.created_at.desc()).limit(10).all()
        
        recent_activity = []
        for b in recent:
            recent_activity.append({
                'id': b.id,
                'type': b.status,
                'message': f'{b.status.title()} booking - {b.customer_name}',
                'created_at': b.created_at.isoformat()
            })
        
        return jsonify({
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
            'total_visitors': total_visitors,
            'conversion_rate': conversion_rate,
            'popular_packages': popular_packages,
            'recent_activity': recent_activity,
            'bookings': [b.to_dict() for b in bookings[:100]]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@tour_bp.route('/tour/admin/reports/export', methods=['GET'])
@login_required
def export_report():
    """Export report in CSV or PDF format"""
    try:
        format_type = request.args.get('format', 'csv')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if not start_date_str or not end_date_str:
            return jsonify({'error': 'Start date and end date are required'}), 400
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
        
        bookings = TourBooking.query.filter(
            TourBooking.created_at >= start_date,
            TourBooking.created_at < end_date
        ).all()
        
        if format_type == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            
            # Headers
            writer.writerow([
                'Reference', 'Customer Name', 'Customer Email', 'Customer Phone',
                'Package', 'Tour Date', 'People Count', 'Total Amount',
                'Status', 'Payment Status', 'Created At'
            ])
            
            # Data
            for b in bookings:
                writer.writerow([
                    b.reference,
                    b.customer_name,
                    b.customer_email,
                    b.customer_phone,
                    b.package.name if b.package else 'N/A',
                    b.tour_date.strftime('%Y-%m-%d %H:%M') if b.tour_date else 'N/A',
                    b.people_count,
                    b.total_amount,
                    b.status,
                    b.payment_status,
                    b.created_at.strftime('%Y-%m-%d %H:%M') if b.created_at else 'N/A'
                ])
            
            response = current_app.response_class(
                output.getvalue(),
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename=report_{start_date_str}_to_{end_date_str}.csv'
                }
            )
            return response
            
        elif format_type == 'pdf':
            if not REPORTLAB_AVAILABLE:
                return jsonify({'error': 'PDF generation not available. Please install reportlab.'}), 500
            
            try:
                # Create filename
                filename = f"revenue_report_{start_date_str}_{end_date_str}.pdf"
                filepath = os.path.join('static', 'reports', filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                doc = SimpleDocTemplate(
                    filepath,
                    pagesize=landscape(A4),
                    rightMargin=72,
                    leftMargin=72,
                    topMargin=72,
                    bottomMargin=72
                )
                
                story = []
                
                # Title
                title_style = ParagraphStyle(
                    'Title',
                    parent=getSampleStyleSheet()['Heading1'],
                    fontSize=20,
                    textColor=colors.HexColor('#1e3a8a'),
                    alignment=TA_CENTER,
                    spaceAfter=20
                )
                
                story.append(Paragraph("Revenue Report", title_style))
                story.append(Paragraph(
                    f"{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}",
                    getSampleStyleSheet()['Normal']
                ))
                story.append(Spacer(1, 20))
                
                # Summary stats
                total_revenue = sum(b.total_amount for b in bookings if b.status == 'completed')
                total_bookings = len(bookings)
                confirmed = len([b for b in bookings if b.status == 'confirmed'])
                pending = len([b for b in bookings if b.status == 'pending'])
                
                summary_data = [
                    ['Total Revenue', 'Total Bookings', 'Confirmed', 'Pending'],
                    [f"KES {total_revenue:,.0f}", str(total_bookings), str(confirmed), str(pending)]
                ]
                
                # ✅ Now inch is properly imported
                summary_table = Table(summary_data, colWidths=[2*inch, 2*inch, 1.5*inch, 1.5*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, 1), [colors.HexColor('#f8fafc')]),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
                ]))
                
                story.append(summary_table)
                story.append(Spacer(1, 30))
                
                # Booking details table
                table_data = [['Ref', 'Customer', 'Package', 'Date', 'People', 'Amount', 'Status']]
                for b in bookings[:20]:  # Limit to 20 for PDF
                    table_data.append([
                        b.reference,
                        b.customer_name[:20] + '...' if len(b.customer_name) > 20 else b.customer_name,
                        b.package.name[:15] + '...' if b.package and len(b.package.name) > 15 else (b.package.name if b.package else 'N/A'),
                        b.tour_date.strftime('%Y-%m-%d') if b.tour_date else 'N/A',
                        str(b.people_count),
                        f"KES {b.total_amount:,.0f}",
                        b.status
                    ])
                
                if len(table_data) > 1:
                    table = Table(table_data, colWidths=[1*inch, 1.2*inch, 1.2*inch, 1*inch, 0.6*inch, 1*inch, 1*inch])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ]))
                    story.append(table)
                
                doc.build(story)
                
                return send_file(
                    filepath,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/pdf'
                )
                
            except Exception as e:
                print(f"❌ PDF generation error: {e}")
                # Fallback to CSV
                import csv
                from io import StringIO
                
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow([
                    'Reference', 'Customer Name', 'Email', 'Phone',
                    'Package', 'Tour Date', 'People', 'Amount', 'Status', 'Payment Status'
                ])
                for b in bookings:
                    writer.writerow([
                        b.reference, b.customer_name, b.customer_email, b.customer_phone,
                        b.package.name if b.package else 'N/A',
                        b.tour_date.strftime('%Y-%m-%d') if b.tour_date else 'N/A',
                        b.people_count, b.total_amount, b.status, b.payment_status
                    ])
                
                response = current_app.response_class(
                    output.getvalue(),
                    mimetype='text/csv',
                    headers={
                        'Content-Disposition': f'attachment; filename=report_{start_date_str}_to_{end_date_str}.csv'
                    }
                )
                return response
        
        return jsonify({'error': 'Invalid format'}), 400
        
    except Exception as e:
        print(f"❌ Report export error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
 
# PAYMENT ROUTES
 

@tour_bp.route('/tour/admin/payments', methods=['GET'])
@login_required
def get_payments():
    """Get all payments with filters"""
    try:
        booking_id = request.args.get('booking_id', type=int)
        status = request.args.get('status')
        
        query = TourPayment.query
        
        if booking_id:
            query = query.filter_by(booking_id=booking_id)
        if status:
            query = query.filter_by(status=status)
        
        payments = query.order_by(TourPayment.created_at.desc()).all()
        
        return jsonify({
            'payments': [p.to_dict() for p in payments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tour_bp.route('/tour/admin/payments/<int:payment_id>', methods=['GET'])
@login_required
def get_payment(payment_id):
    """Get a single payment by ID"""
    try:
        payment = TourPayment.query.get_or_404(payment_id)
        return jsonify(payment.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

 
# TOUR INVOICE ROUTES
 

@tour_bp.route('/tour/admin/invoices/<int:booking_id>', methods=['GET'])
@login_required
def get_invoice(booking_id):
    """Get invoice for a booking"""
    try:
        booking = TourBooking.query.get_or_404(booking_id)
        
        if not current_user.is_super_admin() and not current_user.is_admin() and not current_user.is_tour_manager():
            return jsonify({'error': 'Permission denied'}), 403
        
        invoice = TourInvoice.query.filter_by(booking_id=booking_id).first()
        
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        return jsonify(invoice.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tour_bp.route('/tour/admin/invoices/<int:booking_id>', methods=['POST'])
@login_required
def generate_invoice(booking_id):
    """Generate invoice for a booking"""
    try:
        booking = TourBooking.query.get_or_404(booking_id)
        
        if booking.status not in ['cleared', 'completed']:
            return jsonify({'error': 'Invoice only available for cleared bookings'}), 400
        
        existing = TourInvoice.query.filter_by(booking_id=booking_id).first()
        if existing:
            return jsonify(existing.to_dict()), 200
        
        import random
        import string
        invoice = TourInvoice(
            booking_id=booking.id,
            invoice_number=f"INV-{datetime.utcnow().year}-{''.join(random.choices(string.digits, k=6))}",
            generated_at=datetime.utcnow()
        )
        
        db.session.add(invoice)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Invoice generated successfully',
            'invoice': invoice.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500