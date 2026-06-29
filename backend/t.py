# backend/test_mail.py

from app import app, mail
from flask_mail import Message

with app.app_context():
    try:
        msg = Message(
            subject="Test Email",
            recipients=["your-email@gmail.com"],
            body="This is a test email from Meru Dairy",
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        print("✅ Test email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        print(f"Config: {app.config['MAIL_SERVER']}, {app.config['MAIL_USERNAME']}")