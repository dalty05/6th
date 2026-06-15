# backend/middleware.py
from flask import request, jsonify, current_app
from flask_login import current_user
import re
from functools import lru_cache

# Public routes - no authentication required
PUBLIC_ROUTES = [
    # Health and static
    '/api/health',
    '/api/uploads',
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
    
    # Referral tracking (public)
    '/api/r/',
]

# URL to permission mapping

URL_PERMISSION_MAP = [
    # ========== PRODUCTS ==========
    {
        'pattern': r'^/api/admin/products$',
        'resource': 'products',
        'methods': {
            'GET': 'read',
            'POST': 'create'
        }
    },
    {
        'pattern': r'^/api/admin/products/(\d+)$',
        'resource': 'products',
        'methods': {
            'GET': 'read',
            'PUT': 'update',
            'DELETE': 'delete'
        }
    },
    {
        'pattern': r'^/api/admin/products/(\d+)/upload-image$',
        'resource': 'products',
        'methods': {
            'POST': 'update'
        }
    },
    
    # ========== BLOG ==========
        # Blog - Publish (Super Admin only)
    {
        'pattern': r'^/api/admin/blog/(\d+)/publish$',
        'resource': 'blog',
        'methods': {
            'POST': 'publish'  # ← New action
        }
    },

        {
        'pattern': r'^/api/admin/blog/(\d+)/unpublish$',
        'resource': 'blog',
        'methods': {
            'POST': 'publish'
        }
    },




    {
        'pattern': r'^/api/admin/blog$',
        'resource': 'blog',
        'methods': {
            'GET': 'read',
            'POST': 'create'
        }
    },
    {
        'pattern': r'^/api/admin/blog/(\d+)$',
        'resource': 'blog',
        'methods': {
            'GET': 'read',
            'PUT': 'update',
            'DELETE': 'delete'
        }
    },
    {
        'pattern': r'^/api/admin/blog/(\d+)/upload-image$',
        'resource': 'blog',
        'methods': {
            'POST': 'update'
        }
    },
    {
        'pattern': r'^/api/admin/blog/(\d+)/status$',
        'resource': 'blog',
        'methods': {
            'PUT': 'update'
        }
    },
    
    # ========== JOBS ==========
    {
        'pattern': r'^/api/admin/jobs$',
        'resource': 'jobs',
        'methods': {
            'GET': 'read',
            'POST': 'create'
        }
    },
    {
        'pattern': r'^/api/admin/jobs/(\d+)$',
        'resource': 'jobs',
        'methods': {
            'GET': 'read',
            'PUT': 'update',
            'DELETE': 'delete'
        }
    },
    {
        'pattern': r'^/api/admin/job-categories$',
        'resource': 'jobs',
        'methods': {
            'GET': 'read',
            'POST': 'create'
        }
    },
    {
        'pattern': r'^/api/admin/job-categories/(\d+)$',
        'resource': 'jobs',
        'methods': {
            'PUT': 'update',
            'DELETE': 'delete'
        }
    },
    {
        'pattern': r'^/api/admin/applications$',
        'resource': 'jobs',
        'methods': {
            'GET': 'read'
        }
    },
    {
        'pattern': r'^/api/admin/applications/(\d+)$',
        'resource': 'jobs',
        'methods': {
            'GET': 'read',
            'PUT': 'update'
        }
    },
    {
        'pattern': r'^/api/admin/applications/(\d+)/status$',
        'resource': 'jobs',
        'methods': {
            'PUT': 'update'
        }
    },
    {
        'pattern': r'^/api/admin/applications/(\d+)/reply$',
        'resource': 'jobs',
        'methods': {
            'POST': 'update'
        }
    },
    
    # ========== OUTLETS ==========
    {
        'pattern': r'^/api/admin/outlets$',
        'resource': 'outlets',
        'methods': {
            'GET': 'read',
            'POST': 'create'
        }
    },
    {
        'pattern': r'^/api/admin/outlets/(\d+)$',
        'resource': 'outlets',
        'methods': {
            'GET': 'read',
            'PUT': 'update',
            'DELETE': 'delete'
        }
    },
    
    # ========== USERS ==========
    {
        'pattern': r'^/api/admin/users$',
        'resource': 'users',
        'methods': {
            'GET': 'read',
            'POST': 'create'
        }
    },
    {
        'pattern': r'^/api/admin/users/(\d+)$',
        'resource': 'users',
        'methods': {
            'GET': 'read',
            'PUT': 'update',
            'DELETE': 'delete'
        }
    },
    {
        'pattern': r'^/api/admin/users/(\d+)/approve$',
        'resource': 'users',
        'methods': {
            'POST': 'update'
        }
    },
    {
        'pattern': r'^/api/admin/users/(\d+)/suspend$',
        'resource': 'users',
        'methods': {
            'POST': 'update'
        }
    },
    
    # ========== PARTNERS ==========
    {
        'pattern': r'^/api/admin/partners$',
        'resource': 'partners',
        'methods': {
            'GET': 'read',
            'POST': 'create'
        }
    },
    {
        'pattern': r'^/api/admin/partners/(\d+)$',
        'resource': 'partners',
        'methods': {
            'GET': 'read',
            'PUT': 'update',
            'DELETE': 'delete'
        }
    },
    
    # ========== REFERRALS ==========
    {
        'pattern': r'^/api/referral/links$',
        'resource': 'referrals',
        'methods': {
            'GET': 'read',
            'POST': 'create'
        }
    },
    {
        'pattern': r'^/api/referral/links/(\d+)$',
        'resource': 'referrals',
        'methods': {
            'GET': 'read',
            'PUT': 'update',
            'DELETE': 'delete'
        }
    },
    {
        'pattern': r'^/api/referral/links/(\d+)/clicks$',
        'resource': 'referrals',
        'methods': {
            'GET': 'read'
        }
    },
    {
        'pattern': r'^/api/referral/links/(\d+)/convert$',
        'resource': 'referrals',
        'methods': {
            'POST': 'update'
        }
    },
    {
        'pattern': r'^/api/referral/stats$',
        'resource': 'referrals',
        'methods': {
            'GET': 'read'
        }
    },
    {
        'pattern': r'^/api/referral/top-links$',
        'resource': 'referrals',
        'methods': {
            'GET': 'read'
        }
    },
    {
        'pattern': r'^/api/referral/partner/(\d+)/stats$',
        'resource': 'referrals',
        'methods': {
            'GET': 'read'
        }
    },
    {
        'pattern': r'^/api/referral/admin/links$',
        'resource': 'referrals',
        'methods': {
            'GET': 'read',
            'POST': 'create'
        }
    },
    {
        'pattern': r'^/api/referral/admin/partners$',
        'resource': 'referrals',
        'methods': {
            'GET': 'read'
        }
    },
    
    # ========== STATISTICS ==========
    {
        'pattern': r'^/api/admin/statistics$',
        'resource': 'statistics',
        'methods': {
            'GET': 'read',
            'PUT': 'update'
        }
    },
    
    # ========== SETTINGS ==========
    {
        'pattern': r'^/api/admin/settings$',
        'resource': 'settings',
        'methods': {
            'GET': 'read',
            'PUT': 'update'
        }
    },
    
    # ========== CONTACTS ==========
    {
        'pattern': r'^/api/admin/contacts$',
        'resource': 'contacts',
        'methods': {
            'GET': 'read'
        }
    },
    {
        'pattern': r'^/api/admin/contacts/(\d+)/reply$',
        'resource': 'contacts',
        'methods': {
            'POST': 'update'
        }
    },
    {
        'pattern': r'^/api/admin/contacts/(\d+)/status$',
        'resource': 'contacts',
        'methods': {
            'PUT': 'update'
        }
    },
    
    # ========== PERMISSIONS (Super Admin Only) ==========
    {
        'pattern': r'^/api/permissions/.*$',
        'resource': 'permissions',
        'methods': {
            'GET': 'read',
            'POST': 'create',
            'PUT': 'update',
            'DELETE': 'delete'
        },
        'require_super_admin': True
    },
    
    # ========== UPLOADS ==========
    {
        'pattern': r'^/api/upload$',
        'resource': 'uploads',
        'methods': {
            'POST': 'create'
        }
    },
]

def is_public_route(path):
    """Check if path is publicly accessible without authentication"""
    for public in PUBLIC_ROUTES:
        if path.startswith(public):
            return True
    return False

def match_url_permission(path, method):
    """Find permission rule that matches the URL path"""
    for rule in URL_PERMISSION_MAP:
        if re.match(rule['pattern'], path):
            # Check if rule requires super admin only
            if rule.get('require_super_admin'):
                return rule, True  # True indicates requires super admin
            # Check if method is allowed
            if method in rule['methods']:
                return rule, False
    return None, False

def permission_middleware():
    """
    Middleware to check permissions before request is processed.
    Returns None if allowed, or a Flask response if denied.
    """
    path = request.path
    method = request.method
    
    # Log for debugging (optional - remove in production)
    current_app.logger.debug(f"Permission check: {method} {path}")
    
    # 1. Check public routes
    if is_public_route(path):
        return None
    
    # 2. Skip OPTIONS (CORS preflight)
    if method == 'OPTIONS':
        return None
    
    # 3. Check authentication
    if not current_user.is_authenticated:
        current_app.logger.warning(f"Unauthenticated access attempt: {method} {path}")
        return jsonify({'error': 'Authentication required'}), 401
    
    # 4. Find matching permission rule
    rule, require_super_admin = match_url_permission(path, method)
    
    # 5. If no rule found, default to admin-only access
    if not rule:
        if current_user.role not in ['super_admin', 'admin']:
            current_app.logger.warning(f"Access denied (no rule): {current_user.email} -> {method} {path}")
            return jsonify({'error': 'Access denied'}), 403
        return None
    
    # 6. Check super admin requirement
    if require_super_admin and current_user.role != 'super_admin':
        current_app.logger.warning(f"Super admin required: {current_user.email} -> {method} {path}")
        return jsonify({'error': 'Super admin access required'}), 403
    
    # 7. Check permission using the permission service
    from permission_service import has_permission
    
    resource = rule['resource']
    action = rule['methods'][method]
    
    if not has_permission(current_user, resource, action):
        current_app.logger.warning(f"Permission denied: {current_user.email} -> {resource}.{action} on {method} {path}")
        return jsonify({
            'error': f'Permission denied: {action} on {resource}'
        }), 403
    
    # 8. All checks passed
    return None