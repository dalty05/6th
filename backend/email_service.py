# backend/email_service.py - Complete file

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import os
from datetime import datetime

class EmailService:
    def __init__(self):
        # Load configuration from environment
        self.smtp_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('MAIL_PORT', 587))
        self.smtp_username = os.environ.get('MAIL_USERNAME')
        self.smtp_password = os.environ.get('MAIL_PASSWORD')
        self.from_email = os.environ.get('MAIL_DEFAULT_SENDER', self.smtp_username)
        self.from_name = os.environ.get('APP_NAME', 'Meru Dairy')
        self.enabled = os.environ.get('MAIL_ENABLED', 'true').lower() == 'true'
        
    def _send_email(self, to_email, subject, html_content, text_content=None):
        """Send email using SMTP with proper error handling"""
        if not self.enabled:
            print(f"📧 [MOCK] Email to {to_email}: {subject}")
            return True
        
        if not self.smtp_username or not self.smtp_password:
            print(f"⚠️ Email credentials not configured. Skipping email to {to_email}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = formataddr((self.from_name, self.from_email))
            msg['To'] = to_email
            msg['Reply-To'] = self.from_email
            
            # Add plain text version
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            # Add HTML version
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Email sending failed to {to_email}: {str(e)}")
            return False
    
    # ========== EXISTING METHODS ==========
    
    def send_verification_email(self, user, token, frontend_url):
        """Send email verification link"""
        verification_url = f"{frontend_url}/verify-email?token={token}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Verify Your Email</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #1e3a8a; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #f59e0b; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ font-size: 12px; color: #666; text-align: center; padding: 20px; border-top: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Welcome to Meru Dairy</h2>
                </div>
                <div class="content">
                    <h3>Hello {user.full_name},</h3>
                    <p>Thank you for registering as an administrator. Please verify your email address to continue.</p>
                    <p style="text-align: center;">
                        <a href="{verification_url}" class="button">Verify Email Address</a>
                    </p>
                    <p>This link will expire in 24 hours.</p>
                </div>
                <div class="footer">
                    <p>Meru Central Dairy Co-operative Union Ltd</p>
                    <p>© {datetime.now().year} All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"Welcome to Meru Dairy. Please verify your email: {verification_url}"
        return self._send_email(user.email, "Verify Your Email - Meru Dairy Admin", html, text)
    
    def send_approval_email(self, user, frontend_url):
        """Send account approval notification"""
        login_url = f"{frontend_url}/admin/login"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Account Approved</title>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #10b981; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #1e3a8a; color: white; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Account Approved!</h2>
                </div>
                <div class="content">
                    <h3>Congratulations {user.full_name},</h3>
                    <p>Your administrator account has been approved. You can now log in to the admin portal.</p>
                    <p style="text-align: center;">
                        <a href="{login_url}" class="button">Login to Admin Portal</a>
                    </p>
                    <p>Email: {user.email}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"Your admin account has been approved. Login at {login_url}"
        return self._send_email(user.email, "Account Approved - Meru Dairy Admin", html, text)
    
    def send_otp_email(self, user, otp_code):
        """Send OTP for two-factor authentication"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Login OTP</title>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #1e3a8a; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .otp-code {{ font-size: 36px; font-weight: bold; color: #1e3a8a; text-align: center; padding: 20px; background: #f0f4ff; border-radius: 10px; margin: 20px 0; }}
                .content {{ padding: 30px; background: #f9fafb; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Login Verification Code</h2>
                </div>
                <div class="content">
                    <p>Hello {user.full_name},</p>
                    <p>Your login verification code is:</p>
                    <div class="otp-code">{otp_code}</div>
                    <p>This code will expire in 10 minutes.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"Your OTP code is: {otp_code}. Valid for 10 minutes."
        return self._send_email(user.email, f"Login OTP - Meru Dairy Admin", html, text)
    
    def send_password_reset_email(self, user, token, frontend_url):
        """Send password reset link"""
        reset_url = f"{frontend_url}/reset-password?token={token}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Password Reset</title>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #dc2626; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #dc2626; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Password Reset Request</h2>
                </div>
                <div class="content">
                    <p>Hello {user.full_name},</p>
                    <p>We received a request to reset your password. Click the button below to create a new password:</p>
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button">Reset Password</a>
                    </p>
                    <p>This link will expire in 1 hour.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"Reset your password: {reset_url}"
        return self._send_email(user.email, "Password Reset - Meru Dairy Admin", html, text)
    
    def send_suspension_email(self, user, suspended_by, reason=None):
        """Send account suspension notification"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Account Suspended</title>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #dc2626; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; background: #f9fafb; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Account Suspended</h2>
                </div>
                <div class="content">
                    <p>Dear {user.full_name},</p>
                    <p>Your administrator account has been suspended by {suspended_by.full_name}.</p>
                    {f'<p><strong>Reason:</strong> {reason}</p>' if reason else ''}
                    <p>Please contact the super administrator for more information.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"Your account has been suspended. Contact super admin for details."
        return self._send_email(user.email, "Account Suspended - Meru Dairy Admin", html, text)
    
    def send_contact_reply(self, contact_name, contact_email, subject, reply_message):
        """Send reply to contact message"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Reply to Your Inquiry</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .reply-box {{ background: white; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #f59e0b; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Meru Dairy - Response to Your Inquiry</h2>
                </div>
                <div class="content">
                    <p>Dear {contact_name},</p>
                    <p>Thank you for contacting Meru Central Dairy. Here's our response to your inquiry:</p>
                    <div class="reply-box">
                        <p><strong>Subject:</strong> {subject}</p>
                        <p><strong>Our Response:</strong></p>
                        <p style="white-space: pre-wrap;">{reply_message}</p>
                    </div>
                    <p>If you have any further questions, please don't hesitate to contact us again.</p>
                    <p>Best regards,<br>
                    <strong>Meru Central Dairy Team</strong></p>
                </div>
                <div class="footer">
                    <p>Meru Central Dairy Co-operative Union Ltd</p>
                    <p>Phone: +254 710 901 376 | Email: info@merudairy.co.ke</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"Dear {contact_name},\n\nThank you for contacting Meru Central Dairy. Here's our response to your inquiry:\n\nSubject: {subject}\n\nOur Response:\n{reply_message}\n\nBest regards,\nMeru Central Dairy Team"
        
        return self._send_email(contact_email, f"Re: {subject}", html, text)
    
    def send_welcome_email(self, user, password):
        """Send welcome email with credentials (when super admin creates user)"""
        login_url = f"{os.environ.get('FRONTEND_URL', 'https://propeller-outclass-parsnip.ngrok-free.dev/')}/admin/login"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Welcome to Meru Dairy Admin</title>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #1e3a8a; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .credentials {{ background: #f0f4ff; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #f59e0b; color: white; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Welcome to Meru Dairy Admin Portal</h2>
                </div>
                <div class="content">
                    <p>Hello {user.full_name},</p>
                    <p>Your administrator account has been created. Here are your login credentials:</p>
                    <div class="credentials">
                        <p><strong>Email:</strong> {user.email}</p>
                        <p><strong>Password:</strong> {password}</p>
                    </div>
                    <p style="text-align: center;">
                        <a href="{login_url}" class="button">Login to Your Account</a>
                    </p>
                    <p><strong>Security Note:</strong> Please change your password after first login.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"Welcome! Your account has been created. Email: {user.email}, Password: {password}"
        return self._send_email(user.email, f"Welcome to Meru Dairy Admin Portal", html, text)

    # ========== JOB APPLICATION EMAIL METHODS ==========
    
    def send_job_application_confirmation(self, applicant_name, applicant_email, job_title, application_id):
        """Send confirmation email when job application is submitted"""
        subject = f"Application Received: {job_title} - Meru Dairy"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Application Received</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .reference {{ background: #e0e7ff; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Application Received!</h2>
                    <p>Meru Central Dairy Co-operative Union Ltd</p>
                </div>
                <div class="content">
                    <p>Dear <strong>{applicant_name}</strong>,</p>
                    <p>Thank you for applying for the position of <strong>{job_title}</strong> at Meru Dairy.</p>
                    
                    <div class="reference">
                        <p><strong>Application Reference Number:</strong></p>
                        <h3>APP-{application_id:06d}</h3>
                    </div>
                    
                    <p>Our HR team will review your application within 5-7 business days. If shortlisted, you will be contacted for an interview.</p>
                    
                    <p>We appreciate your interest in joining the Meru Dairy family!</p>
                    <p>Best regards,<br>
                    <strong>HR Department</strong><br>
                    Meru Central Dairy Co-operative Union Ltd</p>
                </div>
                <div class="footer">
                    <p>Meru Central Dairy Co-operative Union Ltd</p>
                    <p>P.O. Box 2919, Meru-Kenya | Tel: 0710 901376</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"Application Received!\n\nDear {applicant_name},\n\nThank you for applying for {job_title}. Your reference number is APP-{application_id:06d}.\n\nBest regards,\nHR Department"
        
        return self._send_email(applicant_email, subject, html, text)
    
    def send_admin_job_notification(self, admin_email, admin_name, applicant_name, job_title, application_id):
        """Send notification to admin when new application is submitted"""
        subject = f"New Job Application: {job_title}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>New Job Application</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .info-box {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #f59e0b; color: white; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>New Job Application Received</h2>
                </div>
                <div class="content">
                    <p>Dear <strong>{admin_name}</strong>,</p>
                    <p>A new application has been submitted for <strong>{job_title}</strong>.</p>
                    
                    <div class="info-box">
                        <p><strong>Applicant:</strong> {applicant_name}</p>
                        <p><strong>Application ID:</strong> APP-{application_id:06d}</p>
                    </div>
                    
                    <p style="text-align: center;">
                        <a href="https://propeller-outclass-parsnip.ngrok-free.dev/" class="button">View Application</a>
                    </p>
                </div>
                <div class="footer">
                    <p>Meru Central Dairy Co-operative Union Ltd</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"New Job Application\n\nDear {admin_name},\n\nA new application has been submitted for {job_title} by {applicant_name}.\n\nLogin to review."
        
        return self._send_email(admin_email, subject, html, text)
    
    def send_job_status_update(self, applicant_name, applicant_email, job_title, status, notes=None):
        """Send email when application status changes"""
        
        status_messages = {
            'reviewed': 'Your application is currently under review by our hiring team.',
            'shortlisted': 'Congratulations! You have been shortlisted for the next stage. Our HR team will contact you soon.',
            'rejected': 'After careful review, we have decided to move forward with other candidates.',
            'hired': 'Congratulations! You have been selected for the position! Our HR team will contact you with offer details.'
        }
        
        message = status_messages.get(status, f'Your application status has been updated to: {status.upper()}')
        subject = f"Application Status Update: {job_title} - Meru Dairy"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Application Status Update</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .status-box {{ background: #e0e7ff; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; }}
                .notes {{ background: white; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Application Status Update</h2>
                </div>
                <div class="content">
                    <p>Dear <strong>{applicant_name}</strong>,</p>
                    
                    <div class="status-box">
                        <h3>Status: {status.upper()}</h3>
                        <p>{message}</p>
                    </div>
                    
                    {f'<div class="notes"><strong>Additional Notes:</strong><br>{notes}</div>' if notes else ''}
                    
                    <p>Position: <strong>{job_title}</strong></p>
                    
                    <p>If you have any questions, please contact us at careers@merudairy.co.ke</p>
                    
                    <p>Best regards,<br>
                    <strong>HR Department</strong><br>
                    Meru Central Dairy Co-operative Union Ltd</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"Application Status Update\n\nDear {applicant_name},\n\nStatus: {status.upper()}\n\n{message}\n\nPosition: {job_title}"
        
        return self._send_email(applicant_email, subject, html, text)
    
    def send_job_admin_reply(self, applicant_name, applicant_email, job_title, reply_message):
        """Send email when admin replies to application"""
        subject = f"Response to Your Application: {job_title} - Meru Dairy"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Response to Your Application</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .reply-box {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Response to Your Application</h2>
                </div>
                <div class="content">
                    <p>Dear <strong>{applicant_name}</strong>,</p>
                    <p>Thank you for your application for <strong>{job_title}</strong>.</p>
                    
                    <div class="reply-box">
                        <p><strong>HR Department's Response:</strong></p>
                        <p style="white-space: pre-wrap;">{reply_message}</p>
                    </div>
                    
                    <p>If you have any further questions, please reply to this email.</p>
                    
                    <p>Best regards,<br>
                    <strong>HR Department</strong><br>
                    Meru Central Dairy Co-operative Union Ltd</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"Response to Your Application\n\nDear {applicant_name},\n\nHR Department's Response:\n{reply_message}"
        
        return self._send_email(applicant_email, subject, html, text)



    def send_password_reset_email_with_new_password(self, user, new_password, frontend_url):
        """Send email with new password when admin resets it"""
        login_url = f"{frontend_url}/admin/login"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Your Password Has Been Reset</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .credentials {{ background: #e0e7ff; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #f59e0b; color: white; text-decoration: none; border-radius: 5px; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Your Password Has Been Reset</h2>
                </div>
                <div class="content">
                    <p>Dear <strong>{user.full_name}</strong>,</p>
                    <p>Your administrator account password has been reset by a system administrator.</p>
                    <div class="credentials">
                        <p><strong>Email:</strong> {user.email}</p>
                        <p><strong>New Password:</strong> <code style="background:#fff;padding:4px 8px;border-radius:4px;">{new_password}</code></p>
                    </div>
                    <p style="text-align: center;">
                        <a href="{login_url}" class="button">Login to Your Account</a>
                    </p>
                    <p><strong>Security Note:</strong> Please change your password after logging in.</p>
                    <p>If you did not request this password reset, please contact your system administrator immediately.</p>
                    <p>Best regards,<br>
                    <strong>Meru Central Dairy Team</strong></p>
                </div>
                <div class="footer">
                    <p>Meru Central Dairy Co-operative Union Ltd</p>
                    <p>P.O. Box 2919, Meru-Kenya | Tel: 0710 901376</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"""
        Your Password Has Been Reset
        
        Dear {user.full_name},
        
        Your password has been reset by a system administrator.
        
        Email: {user.email}
        New Password: {new_password}
        
        Login URL: {login_url}
        
        Please change your password after logging in.
        
        If you did not request this, please contact your system administrator.
        
        Best regards,
        Meru Central Dairy Team
        """
        
        return self._send_email(user.email, "Your Password Has Been Reset - Meru Dairy", html, text)



    def send_email_via_smtp(self, to_email, subject, html_content, text_content=None):
        """Send email directly via SMTP with proper formatting"""
        if not self.enabled:
            print(f"📧 [MOCK] Email to {to_email}: {subject}")
            return True
        
        if not self.smtp_username or not self.smtp_password:
            print(f"⚠️ Email credentials not configured. Skipping email to {to_email}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = formataddr((self.from_name, self.from_email))
            msg['To'] = to_email
            msg['Reply-To'] = self.from_email
            
            # Add plain text version
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            # Add HTML version
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Email sending failed to {to_email}: {str(e)}")
            return False



            # Create singleton instance
email_service = EmailService()