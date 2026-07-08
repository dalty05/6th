# backend/seed_components.py - Update with all components

default_components = [
    # ===== MAIN SECTION =====
    {'key': 'overview', 'label': 'Overview', 'icon': 'fas fa-home', 
     'component_name': 'Overview', 'path': '/admin/dashboard', 'section': 'Main', 'order': 0},
    
    {'key': 'products', 'label': 'Products', 'icon': 'fas fa-box-open', 
     'component_name': 'ProductsManagement', 'path': '/admin/products', 'section': 'Main', 'order': 1},
    
    {'key': 'blog', 'label': 'Blog Posts', 'icon': 'fas fa-newspaper', 
     'component_name': 'BlogManagement', 'path': '/admin/blog', 'section': 'Main', 'order': 2},
    
    {'key': 'jobs', 'label': 'Job Management', 'icon': 'fas fa-briefcase', 
     'component_name': 'JobManagement', 'path': '/admin/jobs', 'section': 'Main', 'order': 3},
    
    {'key': 'outlets', 'label': 'Outlet Locations', 'icon': 'fas fa-map-marker-alt', 
     'component_name': 'OutletManagement', 'path': '/admin/outlets', 'section': 'Main', 'order': 4},
    
    {'key': 'statistics', 'label': 'Analytics', 'icon': 'fas fa-chart-line', 
     'component_name': 'AdvancedAnalytics', 'path': '/admin/statistics', 'section': 'Main', 'order': 5},
    
    {'key': 'contacts', 'label': 'Contact Messages', 'icon': 'fas fa-envelope', 
     'component_name': 'ContactManagement', 'path': '/admin/contacts', 'section': 'Main', 'order': 6},
    
    {'key': 'newsletter', 'label': 'Newsletter', 'icon': 'fas fa-envelope-open-text', 
     'component_name': 'NewsletterManagement', 'path': '/admin/newsletter', 'section': 'Main', 'order': 7},
    
    # ===== TOURS SECTION =====
    {'key': 'tours', 'label': 'Tour Bookings', 'icon': 'fas fa-factory', 
     'component_name': 'TourManagerBookings', 'path': '/admin/tours', 'section': 'Tours', 'order': 0},
    
    {'key': 'tour-packages', 'label': 'Tour Packages', 'icon': 'fas fa-tag', 
     'component_name': 'TourManagerPackages', 'path': '/admin/tour-packages', 'section': 'Tours', 'order': 1},
    
    {'key': 'tour-calendar', 'label': 'Tour Calendar', 'icon': 'fas fa-calendar-alt', 
     'component_name': 'TourManagerCalendar', 'path': '/admin/tour-calendar', 'section': 'Tours', 'order': 2},
    
    {'key': 'tour-payments', 'label': 'Tour Payments', 'icon': 'fas fa-money-bill-wave', 
     'component_name': 'TourManagerPayments', 'path': '/admin/tour-payments', 'section': 'Tours', 'order': 3},
    
    {'key': 'tour-reports', 'label': 'Tour Reports', 'icon': 'fas fa-chart-bar', 
     'component_name': 'TourManagerReports', 'path': '/admin/tour-reports', 'section': 'Tours', 'order': 4},
    
    {'key': 'tour-staff', 'label': 'Tour Staff', 'icon': 'fas fa-users-cog', 
     'component_name': 'TourStaffManagement', 'path': '/admin/tour-staff', 'section': 'Tours', 'order': 5},
    
    # ===== ADMINISTRATION SECTION =====
    {'key': 'users', 'label': 'User Management', 'icon': 'fas fa-users', 
     'component_name': 'UserManagement', 'path': '/admin/users', 'section': 'Administration', 'order': 0},
    
    {'key': 'permissions', 'label': 'Permissions', 'icon': 'fas fa-lock', 
     'component_name': 'PermissionManager', 'path': '/admin/permissions', 'section': 'Administration', 'order': 1},
    
    {'key': 'roles', 'label': 'Role Management', 'icon': 'fas fa-user-tag', 
     'component_name': 'RoleManager', 'path': '/admin/roles', 'section': 'Administration', 'order': 2},
    
    # ===== PARTNER SECTION =====
    {'key': 'partner-dashboard', 'label': 'Partner Dashboard', 'icon': 'fas fa-handshake', 
     'component_name': 'PartnerDashboard', 'path': '/partner/dashboard', 'section': 'Partner', 'order': 0},
    
    {'key': 'partner-links', 'label': 'Referral Links', 'icon': 'fas fa-link', 
     'component_name': 'PartnerReferralLinks', 'path': '/partner/links', 'section': 'Partner', 'order': 1},
    
    {'key': 'partner-analytics', 'label': 'Analytics', 'icon': 'fas fa-chart-line', 
     'component_name': 'PartnerAnalytics', 'path': '/partner/analytics', 'section': 'Partner', 'order': 2},
]