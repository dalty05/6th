import api from './api'
import authService from './auth'

class PermissionService {
  constructor() {
    this.permissions = null
    this.userRole = null
    this.dashboardComponents = []
    this.roleName = null
    this.loaded = false
    this.loadingPromise = null
    this.initialized = false
    this.useDefaults = false // Flag to use defaults if API fails
  }

  async init() {
    if (this.initialized) return
    
    if (authService.isAuthenticated()) {
      await this.loadPermissions()
    } else {
      this.loaded = true
    }
    
    this.initialized = true
  }

  async loadPermissions() {
    if (!authService.isAuthenticated()) {
      this.loaded = true
      return false
    }

    if (this.loadingPromise) {
      return this.loadingPromise
    }

    if (this.loaded && this.permissions && !this.useDefaults) {
      return true
    }

    this.loadingPromise = (async () => {
      try {
        // Get user info first
        const user = authService.getUser()
        const userRole = user?.role || 'user'
        this.userRole = userRole
        
        // Try to load from API - handle 500 gracefully
        try {
          const response = await api.get('/admin/debug/permissions')
          
          if (response.status === 200 && response.data) {
            // Check if the response has an error flag
            if (response.data.success === false) {
              console.warn('Permission API returned error:', response.data.error)
              // Use defaults if there was an error
              this.useDefaults = true
              this.dashboardComponents = this.getDefaultComponentsForRole(userRole)
              this.roleName = userRole.charAt(0).toUpperCase() + userRole.slice(1).replace('_', ' ')
              this.loaded = true
              return true
            }
            
            // Success case
            this.permissions = response.data.permissions || {}
            this.userRole = response.data.role || userRole
            this.dashboardComponents = response.data.components || this.getDefaultComponentsForRole(this.userRole)
            this.roleName = response.data.role_name || userRole.charAt(0).toUpperCase() + userRole.slice(1).replace('_', ' ')
            this.useDefaults = false
            
            // Ensure Super Admin gets all components
            if (this.userRole === 'super_admin') {
              const allComponents = this.getDefaultComponentsForRole('super_admin')
              const existingKeys = new Set(this.dashboardComponents.map(c => c.key))
              for (const comp of allComponents) {
                if (!existingKeys.has(comp.key)) {
                  this.dashboardComponents.push(comp)
                }
              }
            }
            
            this.loaded = true
            return true
          }
        } catch (apiError) {
          console.warn('Failed to load permissions from API, using defaults:', apiError.message)
          this.useDefaults = true
        }
        
        // If we reach here, API failed - use defaults
        if (this.useDefaults || !this.dashboardComponents.length) {
          this.dashboardComponents = this.getDefaultComponentsForRole(userRole)
          this.roleName = userRole.charAt(0).toUpperCase() + userRole.slice(1).replace('_', ' ')
          this.permissions = {}
          this.loaded = true
          return true
        }
        
        this.loaded = true
        return true
        
      } catch (error) {
        console.error('Error in loadPermissions:', error)
        // Ultimate fallback
        const user = authService.getUser()
        const role = user?.role || 'user'
        this.userRole = role
        this.dashboardComponents = this.getDefaultComponentsForRole(role)
        this.roleName = role.charAt(0).toUpperCase() + role.slice(1).replace('_', ' ')
        this.permissions = {}
        this.useDefaults = true
        this.loaded = true
        return true
      } finally {
        this.loadingPromise = null
      }
    })()

    return this.loadingPromise
  }

  //  Get default components for a specific role
  getDefaultComponentsForRole(role) {
    const roleComponents = {
      'super_admin': [
        { key: 'overview', label: 'Overview', icon: 'fas fa-home', section: 'Main' },
        { key: 'products', label: 'Products', icon: 'fas fa-box', section: 'Main' },
        { key: 'blog', label: 'Blog', icon: 'fas fa-blog', section: 'Content' },
        { key: 'jobs', label: 'Jobs', icon: 'fas fa-briefcase', section: 'Content' },
        { key: 'outlets', label: 'Outlets', icon: 'fas fa-store', section: 'Main' },
        { key: 'statistics', label: 'Statistics', icon: 'fas fa-chart-bar', section: 'Analytics' },
        { key: 'contacts', label: 'Contacts', icon: 'fas fa-address-book', section: 'Main' },
        { key: 'newsletter', label: 'Newsletter', icon: 'fas fa-envelope', section: 'Content' },
        { key: 'users', label: 'Users', icon: 'fas fa-users', section: 'Admin' },
        { key: 'permissions', label: 'Permissions', icon: 'fas fa-lock', section: 'Admin' },
        { key: 'roles', label: 'Roles', icon: 'fas fa-user-tag', section: 'Admin' },
        { key: 'tours', label: 'Tours', icon: 'fas fa-map-marked-alt', section: 'Tour' },
        { key: 'tour-packages', label: 'Tour Packages', icon: 'fas fa-boxes', section: 'Tour' },
        { key: 'tour-calendar', label: 'Tour Calendar', icon: 'fas fa-calendar-alt', section: 'Tour' },
        { key: 'tour-payments', label: 'Tour Payments', icon: 'fas fa-credit-card', section: 'Tour' },
        { key: 'tour-reports', label: 'Tour Reports', icon: 'fas fa-file-alt', section: 'Tour' },
        { key: 'tour-staff', label: 'Tour Staff', icon: 'fas fa-user-tie', section: 'Tour' },
        { key: 'partners', label: 'Partners', icon: 'fas fa-handshake', section: 'Partners' },
        { key: 'partner-links', label: 'Partner Links', icon: 'fas fa-link', section: 'Partners' },
        { key: 'partner-analytics', label: 'Partner Analytics', icon: 'fas fa-chart-line', section: 'Partners' },
        { key: 'profile', label: 'Profile', icon: 'fas fa-user', section: 'Admin' },
        { key: 'activities', label: 'Activities', icon: 'fas fa-activity', section: 'Admin' }
      ],
      'admin': [
        { key: 'overview', label: 'Overview', icon: 'fas fa-home', section: 'Main' },
        { key: 'products', label: 'Products', icon: 'fas fa-box', section: 'Main' },
        { key: 'blog', label: 'Blog', icon: 'fas fa-blog', section: 'Content' },
        { key: 'jobs', label: 'Jobs', icon: 'fas fa-briefcase', section: 'Content' },
        { key: 'outlets', label: 'Outlets', icon: 'fas fa-store', section: 'Main' },
        { key: 'statistics', label: 'Statistics', icon: 'fas fa-chart-bar', section: 'Analytics' },
        { key: 'contacts', label: 'Contacts', icon: 'fas fa-address-book', section: 'Main' },
        { key: 'newsletter', label: 'Newsletter', icon: 'fas fa-envelope', section: 'Content' },
        { key: 'users', label: 'Users', icon: 'fas fa-users', section: 'Admin' },
        { key: 'profile', label: 'Profile', icon: 'fas fa-user', section: 'Admin' }
      ],
      'tour_manager': [
        { key: 'overview', label: 'Overview', icon: 'fas fa-home', section: 'Main' },
        { key: 'tours', label: 'Tours', icon: 'fas fa-map-marked-alt', section: 'Tour' },
        { key: 'tour-packages', label: 'Tour Packages', icon: 'fas fa-boxes', section: 'Tour' },
        { key: 'tour-calendar', label: 'Tour Calendar', icon: 'fas fa-calendar-alt', section: 'Tour' },
        { key: 'tour-payments', label: 'Tour Payments', icon: 'fas fa-credit-card', section: 'Tour' },
        { key: 'tour-reports', label: 'Tour Reports', icon: 'fas fa-file-alt', section: 'Tour' },
        { key: 'tour-staff', label: 'Tour Staff', icon: 'fas fa-user-tie', section: 'Tour' },
        { key: 'profile', label: 'Profile', icon: 'fas fa-user', section: 'Admin' }
      ],
      'tour_assistant': [
        { key: 'overview', label: 'Overview', icon: 'fas fa-home', section: 'Main' },
        { key: 'tours', label: 'Tours', icon: 'fas fa-map-marked-alt', section: 'Tour' },
        { key: 'tour-calendar', label: 'Tour Calendar', icon: 'fas fa-calendar-alt', section: 'Tour' },
        { key: 'tour-payments', label: 'Tour Payments', icon: 'fas fa-credit-card', section: 'Tour' },
        { key: 'profile', label: 'Profile', icon: 'fas fa-user', section: 'Admin' }
      ],
      'partner': [
        { key: 'overview', label: 'Overview', icon: 'fas fa-home', section: 'Main' },
        { key: 'partners', label: 'Partners', icon: 'fas fa-handshake', section: 'Partners' },
        { key: 'partner-links', label: 'Partner Links', icon: 'fas fa-link', section: 'Partners' },
        { key: 'partner-analytics', label: 'Partner Analytics', icon: 'fas fa-chart-line', section: 'Partners' },
        { key: 'profile', label: 'Profile', icon: 'fas fa-user', section: 'Admin' }
      ],
      'user': [
        { key: 'overview', label: 'Overview', icon: 'fas fa-home', section: 'Main' },
        { key: 'profile', label: 'Profile', icon: 'fas fa-user', section: 'Admin' }
      ]
    }

    return roleComponents[role] || roleComponents['user']
  }

  can(resource, action = 'read') {
    if (!authService.isAuthenticated()) {
      return false
    }

    if (this.userRole === 'super_admin') {
      return true
    }
    
    if (!this.permissions || !this.permissions[resource]) {
      const hasComponent = this.dashboardComponents.some(c => c.key === resource)
      return hasComponent
    }
    
    return this.permissions[resource][action] === true
  }

  canView(resource) {
    return this.can(resource, 'read')
  }

  canCreate(resource) {
    return this.can(resource, 'create')
  }

  canUpdate(resource) {
    return this.can(resource, 'update')
  }

  canDelete(resource) {
    return this.can(resource, 'delete')
  }

  canViewComponent(componentKey) {
    // ✅ Super Admin can view all components
    if (this.userRole === 'super_admin') {
      return true
    }
    return this.dashboardComponents.some(c => c.key === componentKey)
  }

  // ✅ Get dashboard components (filtered by role)
  getDashboardComponents() {
    // ✅ Return the role-based components
    if (this.dashboardComponents && this.dashboardComponents.length > 0) {
      return this.dashboardComponents
    }
    
    // Fallback: get components based on user's role
    const user = authService.getUser()
    const role = user?.role || 'user'
    return this.getDefaultComponentsForRole(role)
  }

  getRoleName() {
    return this.roleName
  }

  getUserRole() {
    return this.userRole
  }

  isDashboardLoaded() {
    return this.loaded
  }

  clear() {
    this.permissions = null
    this.userRole = null
    this.dashboardComponents = []
    this.roleName = null
    this.loaded = false
    this.loadingPromise = null
    this.initialized = false
  }

  // Component actions
  getComponentActions(componentKey) {
    const actionMap = {
      'overview': ['read'],
      'products': ['create', 'read', 'update', 'delete'],
      'blog': ['create', 'read', 'update', 'delete'],
      'jobs': ['create', 'read', 'update', 'delete'],
      'outlets': ['create', 'read', 'update', 'delete'],
      'statistics': ['read'],
      'contacts': ['read', 'update', 'delete'],
      'newsletter': ['create', 'read', 'update', 'delete'],
      'users': ['create', 'read', 'update', 'delete'],
      'permissions': ['read', 'update'],
      'roles': ['create', 'read', 'update', 'delete'],
      'components': ['create', 'read', 'update', 'delete'],
      'tours': ['create', 'read', 'update', 'delete'],
      'tour-packages': ['create', 'read', 'update', 'delete'],
      'tour-calendar': ['read', 'update'],
      'tour-payments': ['read', 'update'],
      'tour-reports': ['read'],
      'tour-staff': ['read', 'update'],
      'bookings': ['create', 'read', 'update', 'delete', 'approve', 'reject'],
      'tour_settings': ['read', 'update'],
      'partners': ['create', 'read', 'update', 'delete'],
      'partner-links': ['create', 'read', 'update', 'delete'],
      'partner-analytics': ['read'],
      'profile': ['read', 'update'],
      'activities': ['read'],
    }
    return actionMap[componentKey] || ['read']
  }

  // ============================================================
  // ADMIN COMPONENT HELPERS
  // ============================================================

  canViewProducts() { return this.canView('products') }
  canViewBlog() { return this.canView('blog') }
  canViewJobs() { return this.canView('jobs') }
  canViewOutlets() { return this.canView('outlets') }
  canViewUsers() { return this.canView('users') }
  canViewPartners() { return this.canView('partners') }
  canViewReferrals() { return this.canView('referrals') }
  canViewStatistics() { return this.canView('statistics') }
  canViewContacts() { return this.canView('contacts') }
  canViewNewsletter() { return this.canView('newsletter') }
  canViewTours() { return this.canView('tours') }
  canViewBookings() { return this.canView('bookings') }
  canViewRoles() { return this.canView('roles') }
  canViewPermissions() { return this.canView('permissions') }
  canViewActivities() { return this.canView('activities') }
  canViewProfile() { return this.canView('profile') }
}

const permissionService = new PermissionService()
export default permissionService