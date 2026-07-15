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

    if (this.loaded && this.permissions) {
      return true
    }

    this.loadingPromise = (async () => {
      try {
        // ✅ Load permissions from admin debug endpoint
        const permResponse = await api.get('/admin/debug/permissions')
        this.permissions = permResponse.data.permissions
        this.userRole = permResponse.data.role
        
        // ✅ Load dashboard config from admin endpoint
        const configResponse = await api.get('/admin/dashboard/config')
        this.dashboardComponents = configResponse.data.components || []
        this.roleName = configResponse.data.role?.display_name || 'User'
        
        this.loaded = true
        return true
      } catch (error) {
        
        
        if (error.response?.status === 403) {
          this.dashboardComponents = []
          this.roleName = 'User'
          this.loaded = true
          return true
        }
        
        if (error.response?.status === 401) {
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
    if (this.userRole === 'super_admin') {
      return true
    }
    return this.dashboardComponents.some(c => c.key === componentKey)
  }

  getDashboardComponents() {
    return this.dashboardComponents
  }

  getRoleName() {
    return this.roleName
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

  // ============================================================
  // ADMIN COMPONENT HELPERS (Updated paths)
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