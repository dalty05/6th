// frontend/src/services/permissionService.js

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
  }

  // ✅ Initialize only when needed
  async init() {
    if (this.initialized) return
    
    // ✅ Only load if authenticated
    // Note: authService.isAuthenticated() is session-based now.
    if (authService.isAuthenticated()) {
      await this.loadPermissions()
    } else {
      console.log('ℹ️ Not authenticated, permissions will load after login')
      // Don't mark loaded=true here; otherwise it prevents retry after login.
      this.loaded = false
    }

    this.initialized = true
  }

  async loadPermissions() {
    // ✅ Skip if not authenticated
    if (!authService.isAuthenticated()) {
      console.log('⚠️ Not authenticated, skipping permission load')
      return false
    }

    if (this.loadingPromise) {
      return this.loadingPromise
    }

    if (this.loaded && this.permissions) {
      return true
    }

    this.loadingPromise = (async () => {
      try {
        // Load permissions
        const permResponse = await api.get('/debug/permissions')
        this.permissions = permResponse.data.permissions
        this.userRole = permResponse.data.role
        
        // Load dashboard config
        const configResponse = await api.get('/dashboard/config')
        this.dashboardComponents = configResponse.data.components || []
        this.roleName = configResponse.data.role?.name || 'User'
        
        this.loaded = true
        console.log('✅ Permissions and dashboard config loaded:', {
          role: this.roleName,
          components: this.dashboardComponents.length
        })
        return true
      } catch (error) {
        console.error('Failed to load permissions:', error)
        
        // Handle 403 gracefully
        if (error.response?.status === 403) {
          console.warn('⚠️ User does not have permission to access dashboard config')
          this.dashboardComponents = []
          this.roleName = 'User'
          this.loaded = true
          return true
        }
        
        // ✅ Handle 401 (unauthorized) gracefully
        if (error.response?.status === 401) {
          console.log('ℹ️ Session expired - please login again')
          authService.logout()
          this.loaded = true
          return false
        }
        
        this.loaded = false
        return false
      } finally {
        this.loadingPromise = null
      }
    })()

    return this.loadingPromise
  }

  can(resource, action = 'read') {
    // ✅ Check authentication first
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

  // ============================================================
  // DYNAMIC DASHBOARD METHODS
  // ============================================================

  getDashboardComponents() {
    return this.dashboardComponents
  }

  getRoleName() {
    return this.roleName
  }

  canViewComponent(componentKey) {
    if (this.userRole === 'super_admin') {
      return true
    }
    return this.dashboardComponents.some(c => c.key === componentKey)
  }

  getComponentsBySection() {
    const groups = {}
    this.dashboardComponents.forEach(comp => {
      const section = comp.section || 'Main'
      if (!groups[section]) groups[section] = []
      groups[section].push(comp)
    })
    return Object.entries(groups).map(([name, comps]) => ({
      name,
      components: comps.sort((a, b) => (a.order || 0) - (b.order || 0))
    }))
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
    console.debug('Permission cache cleared')
  }

  // ============================================================
  // EXISTING PERMISSION HELPERS
  // ============================================================

  canViewProducts() { return this.canView('products') }
  canCreateProducts() { return this.canCreate('products') }
  canUpdateProducts() { return this.canUpdate('products') }
  canDeleteProducts() { return this.canDelete('products') }

  canViewBlog() { return this.canView('blog') }
  canCreateBlog() { return this.canCreate('blog') }
  canUpdateBlog() { return this.canUpdate('blog') }
  canDeleteBlog() { return this.canDelete('blog') }

  canViewJobs() { return this.canView('jobs') }
  canCreateJobs() { return this.canCreate('jobs') }
  canUpdateJobs() { return this.canUpdate('jobs') }
  canDeleteJobs() { return this.canDelete('jobs') }

  canViewOutlets() { return this.canView('outlets') }
  canCreateOutlets() { return this.canCreate('outlets') }
  canUpdateOutlets() { return this.canUpdate('outlets') }
  canDeleteOutlets() { return this.canDelete('outlets') }

  canViewUsers() { return this.canView('users') }
  canCreateUsers() { return this.canCreate('users') }
  canUpdateUsers() { return this.canUpdate('users') }
  canDeleteUsers() { return this.canDelete('users') }

  canViewPartners() { return this.canView('partners') }
  canCreatePartners() { return this.canCreate('partners') }
  canUpdatePartners() { return this.canUpdate('partners') }
  canDeletePartners() { return this.canDelete('partners') }

  canViewReferrals() { return this.canView('referrals') }
  canCreateReferrals() { return this.canCreate('referrals') }
  canUpdateReferrals() { return this.canUpdate('referrals') }
  canDeleteReferrals() { return this.canDelete('referrals') }

  canViewStatistics() { return this.canView('statistics') }
  canViewContacts() { return this.canView('contacts') }
  canUpdateContacts() { return this.canUpdate('contacts') }
  canDeleteContacts() { return this.canDelete('contacts') }

  canViewPermissions() { return this.userRole === 'super_admin' }
  canManagePermissions() { return this.userRole === 'super_admin' }
  canViewNewsletter() { return this.canView('newsletter') }

  // ============================================================
  // TOUR PERMISSIONS
  // ============================================================

  canViewTours() { return this.canView('tours') || this.canViewComponent('tours') }
  canCreateTours() { return this.canCreate('tours') }
  canUpdateTours() { return this.canUpdate('tours') }
  canDeleteTours() { return this.canDelete('tours') }

  canViewBookings() { return this.canView('bookings') }
  canCreateBookings() { return this.canCreate('bookings') }
  canUpdateBookings() { return this.canUpdate('bookings') }
  canDeleteBookings() { return this.canDelete('bookings') }
  canApproveBookings() { return this.can('bookings', 'approve') }
  canRejectBookings() { return this.can('bookings', 'reject') }

  canViewAvailability() { return this.canView('tours') }
  canUpdateAvailability() { return this.canUpdate('tours') }

  canViewTourSettings() { return this.canView('tour_settings') }
  canUpdateTourSettings() { return this.canUpdate('tour_settings') }

  canManageTours() {
    return this.canCreateTours() || this.canUpdateTours() || this.canDeleteTours()
  }

  canManageBookings() {
    return this.canApproveBookings() || this.canRejectBookings() || this.canUpdateBookings()
  }

  canViewTourData() {
    return this.canViewTours() || this.canViewBookings()
  }

  isTourStaff() {
    return this.canViewTourData()
  }

  // ============================================================
  // RELOAD PERMISSIONS AFTER LOGIN
  // ============================================================

  async refresh() {
    this.clear()
    await this.loadPermissions()
  }

  // ============================================================
  // DEBUG
  // ============================================================

  debugPermissions() {
    console.log('🔍 Permission Debug:')
    console.log('  Initialized:', this.initialized)
    console.log('  Loaded:', this.loaded)
    console.log('  User Role:', this.userRole)
    console.log('  Role Name:', this.roleName)
    console.log('  Components:', this.dashboardComponents.length)
    console.log('  Permissions:', this.permissions)
    console.log('  Authenticated:', authService.isAuthenticated())
  }
}

// Create instance
const permissionService = new PermissionService()



export default permissionService