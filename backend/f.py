#!/usr/bin/env python
"""
Delete Tour Bookings Script
Usage: python delete_booking.py [OPTIONS]

Options:
  --id ID               Delete booking by ID
  --email EMAIL         Delete all bookings for a customer email
  --reference REF       Delete booking by reference
  --status STATUS       Delete all bookings with specific status (pending, confirmed, etc.)
  --date DATE           Delete all bookings on a specific date (YYYY-MM-DD)
  --date-before DATE    Delete all bookings before a date (YYYY-MM-DD)
  --date-after DATE     Delete all bookings after a date (YYYY-MM-DD)
  --all                 Delete ALL bookings (requires confirmation)
  --force               Skip confirmation prompts
  --dry-run             Show what would be deleted without actually deleting
  --help                Show this help message

Examples:
  python delete_booking.py --id 5
  python delete_booking.py --email john@example.com
  python delete_booking.py --reference TU-2024-00123
  python delete_booking.py --status pending
  python delete_booking.py --date 2024-12-25
  python delete_booking.py --date-before 2024-12-01
  python delete_booking.py --all --force
  python delete_booking.py --email john@example.com --dry-run
"""

import sys
import os
import argparse
from datetime import datetime, timedelta
from app import app, db
from models import TourBooking, TourAvailability, TourPayment, TourInvoice

def get_booking_details(booking):
    """Get formatted booking details for display"""
    return {
        'id': booking.id,
        'reference': booking.reference,
        'customer': f"{booking.customer_name} <{booking.customer_email}>",
        'package': booking.package.name if booking.package else 'N/A',
        'date': booking.tour_date.strftime('%Y-%m-%d %H:%M') if booking.tour_date else 'N/A',
        'people': booking.people_count,
        'total': f"KES {booking.total_amount:,.0f}",
        'status': booking.status,
        'payment': booking.payment_status,
        'created': booking.created_at.strftime('%Y-%m-%d %H:%M') if booking.created_at else 'N/A'
    }

def display_bookings(bookings, title="Found Bookings"):
    """Display a list of bookings in a table format"""
    if not bookings:
        print("📭 No bookings found.")
        return
    
    print(f"\n{'='*80}")
    print(f"📋 {title}: {len(bookings)} booking(s)")
    print(f"{'='*80}")
    
    # Header
    print(f"{'ID':>4} | {'Reference':<14} | {'Customer':<25} | {'Status':<12} | {'Date':<12} | {'Total':<10}")
    print("-" * 80)
    
    for booking in bookings:
        details = get_booking_details(booking)
        print(f"{details['id']:>4} | {details['reference']:<14} | {details['customer'][:24]:<25} | "
              f"{details['status']:<12} | {details['date'][:10]:<12} | {details['total']:<10}")
    
    print("="*80)
    
    # Summary
    total_amount = sum(b.total_amount for b in bookings)
    print(f"💰 Total Amount: KES {total_amount:,.0f}")
    print(f"👥 Total People: {sum(b.people_count for b in bookings)}")
    print("="*80)

def confirm_deletion(bookings, dry_run=False):
    """Confirm deletion with user"""
    if dry_run:
        return True
    
    if not bookings:
        return False
    
    display_bookings(bookings, "Bookings to Delete")
    
    response = input(f"\n⚠️  Are you sure you want to delete {len(bookings)} booking(s)? (yes/no): ")
    return response.lower() in ['yes', 'y']

def delete_booking_and_related(booking, dry_run=False):
    """Delete a booking and all related records"""
    if dry_run:
        return True
    
    try:
        # Delete related payments
        payments = TourPayment.query.filter_by(booking_id=booking.id).all()
        for payment in payments:
            db.session.delete(payment)
        
        # Delete related invoice
        invoice = TourInvoice.query.filter_by(booking_id=booking.id).first()
        if invoice:
            db.session.delete(invoice)
        
        # ✅ REMOVED: Update availability - we no longer track booked counts
        # The availability table no longer has a 'booked' field
        # if booking.tour_date:
        #     availability = TourAvailability.query.filter_by(
        #         package_id=booking.package_id,
        #         date=booking.tour_date.date()
        #     ).first()
        #     if availability:
        #         availability.booked = max(0, availability.booked - booking.people_count)
        
        # Delete the booking
        db.session.delete(booking)
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error deleting booking {booking.id}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Delete tour bookings from the database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python delete_booking.py --id 5
  python delete_booking.py --email john@example.com
  python delete_booking.py --reference TU-2024-00123
  python delete_booking.py --status pending
  python delete_booking.py --date 2024-12-25
  python delete_booking.py --date-before 2024-12-01
  python delete_booking.py --all --force
  python delete_booking.py --email john@example.com --dry-run
        """
    )
    
    parser.add_argument('--id', type=int, help='Delete booking by ID')
    parser.add_argument('--email', type=str, help='Delete all bookings for a customer email')
    parser.add_argument('--reference', type=str, help='Delete booking by reference')
    parser.add_argument('--status', type=str, help='Delete all bookings with specific status')
    parser.add_argument('--date', type=str, help='Delete all bookings on a specific date (YYYY-MM-DD)')
    parser.add_argument('--date-before', type=str, help='Delete all bookings before a date (YYYY-MM-DD)')
    parser.add_argument('--date-after', type=str, help='Delete all bookings after a date (YYYY-MM-DD)')
    parser.add_argument('--all', action='store_true', help='Delete ALL bookings')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompts')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    with app.app_context():
        bookings_to_delete = []
        query = None
        
        # Build query based on arguments
        if args.id:
            booking = TourBooking.query.get(args.id)
            if booking:
                bookings_to_delete = [booking]
            else:
                print(f"❌ Booking with ID {args.id} not found")
                sys.exit(1)
        
        elif args.email:
            query = TourBooking.query.filter_by(customer_email=args.email)
            bookings_to_delete = query.all()
            if not bookings_to_delete:
                print(f"📭 No bookings found for email: {args.email}")
                sys.exit(0)
        
        elif args.reference:
            booking = TourBooking.query.filter_by(reference=args.reference).first()
            if booking:
                bookings_to_delete = [booking]
            else:
                print(f"❌ Booking with reference {args.reference} not found")
                sys.exit(1)
        
        elif args.status:
            query = TourBooking.query.filter_by(status=args.status)
            bookings_to_delete = query.all()
            if not bookings_to_delete:
                print(f"📭 No bookings found with status: {args.status}")
                sys.exit(0)
        
        elif args.date:
            try:
                target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
                query = TourBooking.query.filter(db.func.date(TourBooking.tour_date) == target_date)
                bookings_to_delete = query.all()
                if not bookings_to_delete:
                    print(f"📭 No bookings found on date: {args.date}")
                    sys.exit(0)
            except ValueError:
                print(f"❌ Invalid date format: {args.date}. Use YYYY-MM-DD")
                sys.exit(1)
        
        elif args.date_before:
            try:
                target_date = datetime.strptime(args.date_before, '%Y-%m-%d').date()
                query = TourBooking.query.filter(db.func.date(TourBooking.tour_date) < target_date)
                bookings_to_delete = query.all()
                if not bookings_to_delete:
                    print(f"📭 No bookings found before date: {args.date_before}")
                    sys.exit(0)
            except ValueError:
                print(f"❌ Invalid date format: {args.date_before}. Use YYYY-MM-DD")
                sys.exit(1)
        
        elif args.date_after:
            try:
                target_date = datetime.strptime(args.date_after, '%Y-%m-%d').date()
                query = TourBooking.query.filter(db.func.date(TourBooking.tour_date) > target_date)
                bookings_to_delete = query.all()
                if not bookings_to_delete:
                    print(f"📭 No bookings found after date: {args.date_after}")
                    sys.exit(0)
            except ValueError:
                print(f"❌ Invalid date format: {args.date_after}. Use YYYY-MM-DD")
                sys.exit(1)
        
        elif args.all:
            bookings_to_delete = TourBooking.query.all()
            if not bookings_to_delete:
                print("📭 No bookings found in the system")
                sys.exit(0)
        
        else:
            print("❌ No valid option provided. Use --help for usage.")
            sys.exit(1)
        
        # Display what will be deleted
        display_bookings(bookings_to_delete, "Bookings to Delete")
        
        # If dry run, exit after displaying
        if args.dry_run:
            print("\n🔍 DRY RUN - No deletions were performed.")
            sys.exit(0)
        
        # Confirm deletion
        if not args.force:
            response = input(f"\n⚠️  Are you sure you want to delete {len(bookings_to_delete)} booking(s)? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("❌ Deletion cancelled.")
                sys.exit(0)
            
            # Second confirmation for all bookings
            if args.all and len(bookings_to_delete) > 10:
                response = input(f"⚠️  REALLY delete ALL {len(bookings_to_delete)} bookings? This cannot be undone! (type 'DELETE ALL'): ")
                if response != 'DELETE ALL':
                    print("❌ Deletion cancelled.")
                    sys.exit(0)
        
        # Perform deletion
        print(f"\n🔄 Deleting {len(bookings_to_delete)} booking(s)...")
        
        success_count = 0
        failed_count = 0
        
        for booking in bookings_to_delete:
            if delete_booking_and_related(booking, args.dry_run):
                success_count += 1
                print(f"✅ Deleted booking: {booking.reference}")
            else:
                failed_count += 1
                print(f"❌ Failed to delete booking: {booking.reference}")
        
        print(f"\n{'='*50}")
        print(f"📊 Deletion Summary:")
        print(f"  ✅ Successfully deleted: {success_count}")
        print(f"  ❌ Failed to delete: {failed_count}")
        print(f"{'='*50}")

if __name__ == '__main__':
    main()