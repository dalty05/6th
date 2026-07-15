from flask import request, jsonify, current_app
from flask_login import current_user

# ============================================================
# PUBLIC ROUTES 
# ============================================================

PUBLIC_ROUTES = [
    # Health and static
    '/api/health',
    '/uploads',
    
    # Public API endpoints
    '/api/products',
    '/api/products/featured',
    '/api/products/categories',
    '/api/blog',
    '/api/blog/',
    '/api/testimonials',
    '/api/statistics',
    '/api/newsletter/subscribe',
    '/api/contact',
    '/api/jobs',
    '/api/jobs/',
    '/api/job-categories',
    '/api/outlets',
    '/api/outlets/categories',
    
    # Auth endpoints
    '/api/auth/login',
    '/api/auth/register',
    '/api/auth/forgot-password',
    '/api/auth/reset-password',
    '/api/auth/verify-email',
    '/api/auth/check-session',
    
    # Referral tracking (public)
    '/api/r/',
    
    # Tour public routes
    '/api/tour/packages',
    '/api/tour/availability',
    '/api/tour/booking',
]

# ============================================================
# BYPASS ROUTES 
# ============================================================

BYPASS_ROUTES = [
    '/api/admin/check-auth',
    '/api/admin/check',
    '/api/admin/check-auth',
    '/api/auth/logout',
    '/api/admin/debug/permissions',
    '/api/auth/login/test',
    '/api/dashboard/config',
    '/api/admin/dashboard/config',
    '/api/admin/permissions/me',
    '/api/admin/permissions/check',
    '/api/admin/upload',
]

# ============================================================
# PERMISSION MIDDLEWARE
# ============================================================

def permission_middleware():
    """
    Unified permission middleware - handles authentication only.
    Permission checks are now handled in each route using @require_permission decorator.
    """
    path = request.path
    method = request.method
    
    if is_public_route(path):
        return None
    
    if method == 'OPTIONS':
        return None
    
    if path in BYPASS_ROUTES:
        return None
    
    # 4. Check authentication
    if not current_user.is_authenticated:
        current_app.logger.warning(f"🔒 Unauthenticated access attempt: {method} {path}")
        return jsonify({'error': 'Authentication required'}), 401
    
    # 5. Log authenticated access
    current_app.logger.debug(f"✅ Authenticated: {current_user.email} -> {method} {path}")
        
    return None

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def is_public_route(path):
    """Check if path is publicly accessible without authentication"""
    for public in PUBLIC_ROUTES:
        if path.startswith(public):
            return True
    return False

def is_bypass_route(path):
    """Check if path is a bypass route"""
    return path in BYPASS_ROUTES