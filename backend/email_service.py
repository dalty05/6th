import os
import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv

dotenv_candidates = [
    os.path.join(os.path.dirname(__file__), '.env'),
    os.path.join(os.path.dirname(__file__), 'dotenv.env'),
    # repo root .env (one level up from backend/)
    os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),
]

dotenv_loaded_any = False
for p in dotenv_candidates:
    if os.path.exists(p):
        load_dotenv(p, override=False)
        dotenv_loaded_any = True
        break


class EmailService:
    def __init__(self):
        self.mail_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        self.mail_port = int(os.environ.get('MAIL_PORT', 587))
        self.mail_use_tls = os.environ.get('MAIL_USE_TLS', 'True').lower() in ('1', 'true', 'yes')
        self.mail_use_ssl = os.environ.get('MAIL_USE_SSL', 'False').lower() in ('1', 'true', 'yes')
        self.mail_username = os.environ.get('MAIL_USERNAME')
        self.mail_password = os.environ.get('MAIL_PASSWORD')
        self.from_email = os.environ.get('EMAIL_FROM') or os.environ.get('MAIL_DEFAULT_SENDER') or self.mail_username or 'noreply@example.com'
        self.app_name = os.environ.get('APP_NAME', 'MeruDairy')
        self.environment = os.environ.get('ENVIRONMENT', 'development')

        self._configured = {
            'mail_server': self.mail_server,
            'mail_port': self.mail_port,
            'mail_use_tls': self.mail_use_tls,
            'mail_use_ssl': self.mail_use_ssl,
            'mail_username': bool(self.mail_username),
            'from_email': self.from_email,
            'app_name': self.app_name,
            'environment': self.environment,
        }
    
    def _create_message(self, to_email, subject, html_content, text_content=None):
        message = EmailMessage()
        message['Subject'] = subject
        message['From'] = self.from_email
        message['To'] = to_email
        if text_content:
            message.set_content(text_content)
        message.add_alternative(html_content, subtype='html')
        return message

    def send_email(self, to_email, subject, html_content, text_content=None):
        """Send email using SMTP"""
        if not self.mail_username or not self.mail_password:
            print('SMTP credentials missing: MAIL_USERNAME or MAIL_PASSWORD not set')
            return False

        message = self._create_message(to_email, subject, html_content, text_content)

        try:
            if self.mail_use_ssl:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.mail_server, self.mail_port, context=context) as server:
                    server.login(self.mail_username, self.mail_password)
                    server.send_message(message)
            else:
                with smtplib.SMTP(self.mail_server, self.mail_port) as server:
                    if self.mail_use_tls:
                        server.starttls(context=ssl.create_default_context())
                    server.login(self.mail_username, self.mail_password)
                    server.send_message(message)
            return True
        except Exception as e:
            print(f'SMTP send failed: {e}')
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