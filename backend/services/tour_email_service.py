# backend/services/tour_email_service.py
"""
Tour Email Service - Handles all tour-related email notifications
Uses direct SMTP (same as email_service.py)
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from datetime import datetime
from flask import render_template

class TourEmailService:
    """Service for sending tour-related emails using direct SMTP"""
    
    def __init__(self):
        """Initialize email configuration from environment"""
        self.smtp_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('MAIL_PORT', 587))
        self.smtp_username = os.environ.get('MAIL_USERNAME')
        self.smtp_password = os.environ.get('MAIL_PASSWORD')
        self.from_email = os.environ.get('MAIL_DEFAULT_SENDER', self.smtp_username)
        self.from_name = os.environ.get('APP_NAME', 'Mount Kenya Milk')
        
        # Check if credentials are available
        has_credentials = self.smtp_username and self.smtp_password
        mail_enabled = os.environ.get('MAIL_ENABLED', 'true').lower()
        self.enabled = has_credentials and mail_enabled != 'false'
        
        if self.enabled:
            print(f"✅ TourEmailService: Email ENABLED with SMTP: {self.smtp_server}")
        else:
            print(f"⚠️ TourEmailService: Email DISABLED - logging mode")
    
    def _send_email(self, to_email, subject, html_content):
        """Send email using direct SMTP"""
        
        print(f"\n{'='*60}")
        print(f"📧 [EMAIL] Subject: {subject}")
        print(f"   To: {to_email}")
        print(f"   From: {self.from_name} <{self.from_email}>")
        print(f"   Enabled: {self.enabled}")
        
        if not self.enabled:
            print(f"📧 [EMAIL LOG] Email would be sent but is disabled")
            print(f"{'='*60}\n")
            return True
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = formataddr((self.from_name, self.from_email))
            msg['To'] = to_email
            msg['Subject'] = subject
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully: {subject} to {to_email}")
            print(f"{'='*60}\n")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            print(f"{'='*60}\n")
            return False
    
    def send_booking_received(self, booking):
        """Send booking received confirmation email"""
        subject = f"Booking Received - {booking.reference}"
        
        package_name = booking.package.name if booking.package else 'Factory Tour'
        tour_date = booking.tour_date.strftime('%A, %B %d, %Y at %I:%M %p') if booking.tour_date else 'Date TBD'
        commitment_percentage = booking.package.commitment_percentage if booking.package else 30
        
        try:
            html = render_template(
                'emails/tour/booking_received.html',
                customer_name=booking.customer_name,
                booking_reference=booking.reference,
                package_name=package_name,
                tour_date=tour_date,
                people_count=booking.people_count,
                total_amount=f"{booking.total_amount:,.0f}",
                commitment_amount=f"{booking.commitment_amount:,.0f}",
                commitment_percentage=commitment_percentage,
                current_year=datetime.utcnow().year
            )
        except Exception as e:
            print(f"Template error: {e}, using fallback HTML")
            html = self._get_booking_received_html(booking, package_name, tour_date, commitment_percentage)
        
        return self._send_email(booking.customer_email, subject, html)
    
    def _get_booking_received_html(self, booking, package_name, tour_date, commitment_percentage):
        return f"""
        <h1>Booking Received!</h1>
        <p>Dear {booking.customer_name},</p>
        <p>Thank you for submitting a factory tour booking with Mount Kenya Milk!</p>
        <p><strong>Booking Reference:</strong> {booking.reference}</p>
        <p><strong>Package:</strong> {package_name}</p>
        <p><strong>Date:</strong> {tour_date}</p>
        <p><strong>People:</strong> {booking.people_count}</p>
        <p><strong>Total Amount:</strong> KES {booking.total_amount:,.0f}</p>
        <p><strong>Deposit Required ({commitment_percentage}%):</strong> KES {booking.commitment_amount:,.0f}</p>
        <p>Our team will review your booking within 24 hours.</p>
        <p><strong>The Mount Kenya Milk Team</strong></p>
        """
    
    def send_booking_confirmed(self, booking):
        """Send booking confirmed email"""
        subject = f"Booking Confirmed - {booking.reference}"
        
        package_name = booking.package.name if booking.package else 'Factory Tour'
        tour_date = booking.tour_date.strftime('%A, %B %d, %Y at %I:%M %p') if booking.tour_date else 'Date TBD'
        
        try:
            html = render_template(
                'emails/tour/booking_confirmed.html',
                customer_name=booking.customer_name,
                booking_reference=booking.reference,
                package_name=package_name,
                tour_date=tour_date,
                people_count=booking.people_count,
                total_amount=f"{booking.total_amount:,.0f}",
                commitment_amount=f"{booking.commitment_amount:,.0f}",
                current_year=datetime.utcnow().year
            )
        except Exception as e:
            print(f"Template error: {e}, using fallback HTML")
            html = self._get_booking_confirmed_html(booking, package_name, tour_date)
        
        return self._send_email(booking.customer_email, subject, html)
    
    def _get_booking_confirmed_html(self, booking, package_name, tour_date):
        return f"""
        <h1>Booking Confirmed!</h1>
        <p>Dear {booking.customer_name},</p>
        <p>Great news! Your factory tour booking has been CONFIRMED!</p>
        <p><strong>Booking Reference:</strong> {booking.reference}</p>
        <p><strong>Package:</strong> {package_name}</p>
        <p><strong>Date:</strong> {tour_date}</p>
        <p><strong>People:</strong> {booking.people_count}</p>
        <p><strong>Deposit Required:</strong> KES {booking.commitment_amount:,.0f}</p>
        <p><strong>The Mount Kenya Milk Team</strong></p>
        """
    
    def send_booking_rejected(self, booking, reason):
        """Send booking rejected email"""
        subject = f"Booking Update - {booking.reference}"
        
        package_name = booking.package.name if booking.package else 'Factory Tour'
        tour_date = booking.tour_date.strftime('%A, %B %d, %Y at %I:%M %p') if booking.tour_date else 'Date TBD'
        
        try:
            html = render_template(
                'emails/tour/booking_rejected.html',
                customer_name=booking.customer_name,
                booking_reference=booking.reference,
                package_name=package_name,
                tour_date=tour_date,
                people_count=booking.people_count,
                rejection_reason=reason or 'No reason provided',
                current_year=datetime.utcnow().year
            )
        except Exception as e:
            print(f"Template error: {e}, using fallback HTML")
            html = self._get_booking_rejected_html(booking, package_name, tour_date, reason)
        
        return self._send_email(booking.customer_email, subject, html)
    
    def _get_booking_rejected_html(self, booking, package_name, tour_date, reason):
        return f"""
        <h1>Booking Update</h1>
        <p>Dear {booking.customer_name},</p>
        <p>We regret to inform you that your booking {booking.reference} has been rejected.</p>
        <p><strong>Package:</strong> {package_name}</p>
        <p><strong>Date:</strong> {tour_date}</p>
        <p><strong>Reason:</strong> {reason or 'No reason provided'}</p>
        <p><strong>The Mount Kenya Milk Team</strong></p>
        """
    
    def send_payment_received(self, booking, payment_amount, payment_type):
        """Send payment received confirmation email"""
        subject = f"Payment Received - {booking.reference}"
        
        remaining_balance = booking.total_amount - payment_amount
        
        try:
            html = render_template(
                'emails/tour/payment_received.html',
                customer_name=booking.customer_name,
                booking_reference=booking.reference,
                payment_amount=f"{payment_amount:,.0f}",
                payment_type=payment_type,
                total_amount=f"{booking.total_amount:,.0f}",
                remaining_balance=f"{remaining_balance:,.0f}",
                current_year=datetime.utcnow().year
            )
        except Exception as e:
            print(f"Template error: {e}, using fallback HTML")
            html = self._get_payment_received_html(booking, payment_amount, payment_type, remaining_balance)
        
        return self._send_email(booking.customer_email, subject, html)
    
    def _get_payment_received_html(self, booking, payment_amount, payment_type, remaining_balance):
        return f"""
        <h1>Payment Received!</h1>
        <p>Dear {booking.customer_name},</p>
        <p>We have received your payment of KES {payment_amount:,.0f} for booking {booking.reference}.</p>
        <p><strong>Payment Type:</strong> {payment_type}</p>
        <p><strong>Remaining Balance:</strong> KES {remaining_balance:,.0f}</p>
        <p>Thank you for your payment!</p>
        <p><strong>The Mount Kenya Milk Team</strong></p>
        """
    
    def send_booking_cancelled(self, booking, reason):
        """Send booking cancelled email"""
        subject = f"Booking Cancelled - {booking.reference}"
        
        html = f"""
        <h1>Booking Cancelled</h1>
        <p>Dear {booking.customer_name},</p>
        <p>Your booking {booking.reference} has been cancelled.</p>
        <p><strong>Reason:</strong> {reason or 'No reason provided'}</p>
        <p><strong>The Mount Kenya Milk Team</strong></p>
        """
        
        return self._send_email(booking.customer_email, subject, html)