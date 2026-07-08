from flask import request, jsonify, current_app
from flask_login import current_user
import re
from functools import lru_cache
from permission_service import has_permission, is_custom_role, SYSTEM_ROLES


# Public routes 
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
    # Tour public routes
    '/api/tour/packages',
    '/api/tour/availability',
    '/api/tour/booking',
]



URL_PERMISSION_MAP = [

        # ========== ACTIVITIES ==========
    {
        'pattern': r'^/api/admin/activities$',
        'resource': 'activities',
        'methods': {
            'GET': 'read'
        }
    },
    {
        'pattern': r'^/api/admin/activities/(\d+)$',
        'resource': 'activities',
        'methods': {
            'GET': 'read'
        }
    },




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
    {
        'pattern': r'^/api/admin/blog/(\d+)/publish$',
        'resource': 'blog',
        'methods': {
            'POST': 'update'
        }
    },
    {
        'pattern': r'^/api/admin/blog/(\d+)/unpublish$',
        'resource': 'blog',
        'methods': {
            'POST': 'update'
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
    {
        'pattern': r'^/api/admin/users/(\d+)/activate$',
        'resource': 'users',
        'methods': {
            'POST': 'update'
        }
    },
    {
        'pattern': r'^/api/admin/users/(\d+)/reset-password$',
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
    
    # ========== PROFILE ==========
    {
        'pattern': r'^/api/admin/profile$',
        'resource': 'profile',
        'methods': {
            'GET': 'read',
            'PUT': 'update'
        }
    },
    {
        'pattern': r'^/api/admin/change-password$',
        'resource': 'profile',
        'methods': {
            'PUT': 'update'
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
    
    # ========== CONTACTS ==========
    {
        'pattern': r'^/api/admin/contacts$',
        'resource': 'contacts',
        'methods': {
            'GET': 'read',
            'POST': 'create'
        }
    },
    {
        'pattern': r'^/api/admin/contacts/stats$',
        'resource': 'contacts',
        'methods': {
            'GET': 'read'
        }
    },
    {
        'pattern': r'^/api/admin/contacts/(\d+)$',
        'resource': 'contacts',
        'methods': {
            'GET': 'read',
            'PUT': 'update',
            'DELETE': 'delete'
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
    
    # ========== NEWSLETTER ==========
    {
        'pattern': r'^/api/admin/newsletter/subscribers$',
        'resource': 'newsletter',
        'methods': {
            'GET': 'read'
        }
    },
    {
        'pattern': r'^/api/admin/newsletter/subscribers/stats$',
        'resource': 'newsletter',
        'methods': {
            'GET': 'read'
        }
    },
    {
        'pattern': r'^/api/admin/newsletter/subscribers/(\d+)$',
        'resource': 'newsletter',
        'methods': {
            'DELETE': 'delete'
        }
    },
    {
        'pattern': r'^/api/admin/newsletter/subscribers/(\d+)/toggle$',
        'resource': 'newsletter',
        'methods': {
            'PUT': 'update'
        }
    },
    {
        'pattern': r'^/api/admin/newsletter/send$',
        'resource': 'newsletter',
        'methods': {
            'POST': 'create'
        }
    },
    {
        'pattern': r'^/api/admin/newsletter/export$',
        'resource': 'newsletter',
        'methods': {
            'GET': 'read'
        }
    },
    
    # ========== PERMISSIONS ==========
    {
        'pattern': r'^/api/permissions/me$',
        'resource': 'permissions',
        'methods': {
            'GET': 'read'
        }
        # No super admin requirement - any authenticated user
    },
    {
        'pattern': r'^/api/permissions/resources$',
        'resource': 'permissions',
        'methods': {
            'GET': 'read'
        },
        'require_super_admin': True
    },
    {
        'pattern': r'^/api/permissions/users/.*$',
        'resource': 'permissions',
        'methods': {
            'GET': 'read',
            'POST': 'create',
            'PUT': 'update',
            'DELETE': 'delete'
        },
        'require_super_admin': True
    },
    {
        'pattern': r'^/api/permissions/check$',
        'resource': 'permissions',
        'methods': {
            'POST': 'read'
        }
        # No super admin requirement
    },
    
    # ========== DASHBOARD ==========
    {
        'pattern': r'^/api/dashboard/config$',
        'resource': 'dashboard',
        'methods': {
            'GET': 'read'
        }
        # No super admin requirement - any authenticated user
    },
    
    # ========== TOUR MANAGEMENT ==========
    # Tour Packages
    {
        'pattern': r'^/api/tour/admin/packages$',
        'resource': 'tours',
        'methods': {
            'GET': 'read',
            'POST': 'create'
        }
    },
    {
        'pattern': r'^/api/tour/admin/packages/(\d+)$',
        'resource': 'tours',
        'methods': {
            'GET': 'read',
            'PUT': 'update',
            'DELETE': 'delete'
        }
    },
    
    # Tour Bookings
    {
        'pattern': r'^/api/tour/admin/bookings$',
        'resource': 'bookings',
        'methods': {
            'GET': 'read'
        }
    },
    {
        'pattern': r'^/api/tour/admin/bookings/(\d+)$',
        'resource': 'bookings',
        'methods': {
            'GET': 'read',
            'PUT': 'update'
        }
    },
    {
        'pattern': r'^/api/tour/admin/bookings/(\d+)/status$',
        'resource': 'bookings',
        'methods': {
            'PUT': 'update'
        }
    },
    {
        'pattern': r'^/api/tour/admin/bookings/(\d+)/change-request$',
        'resource': 'bookings',
        'methods': {
            'POST': 'update'
        }
    },
    {
        'pattern': r'^/api/tour/admin/bookings/(\d+)/payment$',
        'resource': 'bookings',
        'methods': {
            'PUT': 'update'
        }
    },
    {
        'pattern': r'^/api/tour/admin/bookings/(\d+)/certificate$',
        'resource': 'bookings',
        'methods': {
            'GET': 'read'
        }
    },
    
    # Tour Availability
    {
        'pattern': r'^/api/tour/admin/availability$',
        'resource': 'tours',
        'methods': {
            'PUT': 'update'
        }
    },
    
    # Tour Dashboard & Reports
    {
        'pattern': r'^/api/tour/admin/dashboard/stats$',
        'resource': 'tours',
        'methods': {
            'GET': 'read'
        }
    },
    {
        'pattern': r'^/api/tour/admin/reports/summary$',
        'resource': 'tours',
        'methods': {
            'GET': 'read'
        }
    },
    {
        'pattern': r'^/api/tour/admin/reports/export$',
        'resource': 'tours',
        'methods': {
            'GET': 'read'
        }
    },
    
    # Tour Payments
    {
        'pattern': r'^/api/tour/admin/payments$',
        'resource': 'bookings',
        'methods': {
            'GET': 'read'
        }
    },
    {
        'pattern': r'^/api/tour/admin/payments/(\d+)$',
        'resource': 'bookings',
        'methods': {
            'GET': 'read'
        }
    },
    
    # Tour Invoices
    {
        'pattern': r'^/api/tour/admin/invoices/(\d+)$',
        'resource': 'bookings',
        'methods': {
            'GET': 'read',
            'POST': 'create'
        }
    },
    
    # ========== REFERRALS ==========

    






    {
        'pattern': r'^/api/referral/analytics/partner$',
        'resource': 'referrals',
        'methods': {
            'GET': 'read'
        }
    },
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
        'pattern': r'^/api/referral/analytics/.*$',
        'resource': 'referrals',
        'methods': {
            'GET': 'read'
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





# backend/middleware.py

def permission_middleware():
    path = request.path
    method = request.method
    
    # Log for debugging
    current_app.logger.debug(f"Permission check: {method} {path}")
    
    # 1. Check public routes
    if is_public_route(path):
        return None
    
    # 2. Skip OPTIONS (CORS preflight)
    if method == 'OPTIONS':
        return None
    
    # ============================================================
    #  BYPASS LIST - These endpoints are allowed without permission checks
    # ============================================================
    bypass_paths = [
        '/api/admin/check-auth',
        '/api/admin/check',
        '/api/auth/check-session',
        '/api/auth/logout',
        '/api/debug/permissions',
        '/api/auth/login/test',
        '/api/dashboard/config',
        '/api/permissions/me',  
        '/api/permissions/check',  
    ]
    
    if path in bypass_paths:
        return None
    
    # 3. Check authentication
    if not current_user.is_authenticated:
        current_app.logger.warning(f"Unauthenticated access attempt: {method} {path}")
        return jsonify({'error': 'Authentication required'}), 401
    # ✅ Log if custom role
    if is_custom_role(current_user.role):
        current_app.logger.info(f"🔍 Custom role detected: {current_user.role} for {current_user.email}")


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
    resource = rule['resource']
    action = rule['methods'][method]
    
    # ✅ Check permission
    if has_permission(current_user, resource, action):
        # ✅ Permission granted - allow the request
        current_app.logger.debug(f"✅ Permission granted: {current_user.email} -> {resource}.{action}")
        return None
    
    # ============================================================
    # FALLBACK: Permission denied - check dynamic components
    # ============================================================
    
    current_app.logger.warning(
        f"Permission denied: {current_user.email} -> {resource}.{action} on {method} {path}"
    )
    
    # Check if this is a dynamic component route
    from models import DashboardComponent
    component = DashboardComponent.query.filter_by(path=path).first()

    # If we didn't find by exact path, try stripping the '/api' prefix
    if not component and path.startswith('/api'):
        normalized_path = path[len('/api'):]
        component = DashboardComponent.query.filter_by(path=normalized_path).first()

    # FINAL FALLBACK: some admin endpoints map to resource names
    if not component:
        component = DashboardComponent.query.filter_by(key=resource).first()

    if component:
        role_id = current_user.role_id
        if not role_id and getattr(current_user, 'role', None):
            from sqlalchemy import func
            from models import Role
            role = Role.query.filter(func.lower(Role.name) == current_user.role.lower()).first()
            if role:
                role_id = role.id

        if role_id:
            from models import RoleComponent
            role_component = RoleComponent.query.filter_by(
                role_id=role_id,
                component_id=component.id
            ).first()
            if role_component:
                # User has access via dynamic role
                current_app.logger.info(f"✅ Dynamic component access granted: {current_user.email} -> {component.key}")
                return None
    # Default to admin-only access for system roles
        if current_user.role not in ['super_admin', 'admin'] and not is_custom_role(current_user.role):
            current_app.logger.warning(f"Access denied (no rule): {current_user.email} -> {method} {path}")
            return jsonify({'error': 'Access denied'}), 403
        return None



