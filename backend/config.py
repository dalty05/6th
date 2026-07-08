

class Config:
    # Session configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SESSION_COOKIE_SECURE = True  # In production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)