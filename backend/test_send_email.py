from email_service import EmailService

svc = EmailService()
print('Configured:', svc._configured)
print('Has client:', svc.client is not None)
res = svc.send_email(svc.from_email, 'Meru Test Email', '<p>This is a test from Meru backend.</p>', 'This is a test')
print('Send result:', res)
