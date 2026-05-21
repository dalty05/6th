import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from flask import render_template_string

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(dotenv_path):
    dotenv_path = os.path.join(os.path.dirname(__file__), 'dotenv.env')
load_dotenv(dotenv_path)

class EmailService:
    def __init__(self):
        self.smtp_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('MAIL_PORT', 587))
        self.smtp_username = os.environ.get('MAIL_USERNAME')
        self.smtp_password = os.environ.get('MAIL_PASSWORD')
        self.from_email = os.environ.get('MAIL_DEFAULT_SENDER', 'oyigodalton@gmail.com')
    
    def send_email(self, to_email, subject, html_content, text_content=None):
        """Send email using SMTP"""
        if not self.smtp_username or not self.smtp_password:
            print("Email credentials not configured")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Plain text version
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            # HTML version
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False
    
    def send_verification_email(self, user, token, frontend_url):
        """Send email verification link"""
        verification_url = f"{frontend_url}/verify-email?token={token}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #1e3a8a; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #1e3a8a; color: white; text-decoration: none; border-radius: 5px; }}
                .footer {{ font-size: 12px; color: #666; text-align: center; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Welcome to Meru Dairy Admin Portal</h2>
                </div>
                <div class="content">
                    <h3>Hello {user.full_name},</h3>
                    <p>Thank you for registering as an administrator. Please verify your email address by clicking the button below:</p>
                    <p style="text-align: center;"><a href="{verification_url}" class="button">Verify Email Address</a></p>
                    <p>Or copy this link: <br>{verification_url}</p>
                    <p>This link will expire in 24 hours.</p>
                    <p>After verification, a super admin will review and approve your account.</p>
                </div>
                <div class="footer">
                    <p>Meru Central Dairy Co-operative Union Ltd</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"Welcome to Meru Dairy Admin Portal. Please verify your email: {verification_url}"
        return self.send_email(user.email, "Verify Your Email - Meru Dairy Admin", html, text)
    
    def send_approval_email(self, user, frontend_url):
        """Send approval notification"""
        login_url = f"{frontend_url}/admin/login"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #10b981; color: white; padding: 20px; text-align: center; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #1e3a8a; color: white; text-decoration: none; border-radius: 5px; }}
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
                    <p style="text-align: center;"><a href="{login_url}" class="button">Login to Admin Portal</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"Your admin account has been approved. Login at {login_url}"
        return self.send_email(user.email, "Account Approved - Meru Dairy Admin", html, text)
    
    def send_otp_email(self, user, otp_code):
        """Send OTP for 2FA"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .otp-code {{ font-size: 32px; font-weight: bold; color: #1e3a8a; text-align: center; padding: 20px; background: #f0f4ff; border-radius: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h3>Your Login OTP Code</h3>
                <div class="otp-code">{otp_code}</div>
                <p>This code will expire in 10 minutes.</p>
                <p>If you didn't request this, please ignore this email.</p>
            </div>
        </body>
        </html>
        """
        
        text = f"Your OTP code is: {otp_code}. Valid for 10 minutes."
        return self.send_email(user.email, f"Login OTP - Meru Dairy Admin", html, text)
    
    def send_password_reset_email(self, user, token, frontend_url):
        """Send password reset link"""
        reset_url = f"{frontend_url}/reset-password?token={token}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #1e3a8a; color: white; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h3>Password Reset Request</h3>
                <p>Hello {user.full_name},</p>
                <p>Click the button below to reset your password:</p>
                <p style="text-align: center;"><a href="{reset_url}" class="button">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
            </div>
        </body>
        </html>
        """
        
        text = f"Reset your password: {reset_url}"
        return self.send_email(user.email, "Password Reset - Meru Dairy Admin", html, text)
    
    def send_suspension_email(self, user, suspended_by, reason=None):
        """Send suspension notification"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #dc2626; color: white; padding: 20px; text-align: center; }}
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
                    {f'<p>Reason: {reason}</p>' if reason else ''}
                    <p>Please contact the super administrator for more information.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"Your account has been suspended. Contact super admin for details."
        return self.send_email(user.email, "Account Suspended - Meru Dairy Admin", html, text)