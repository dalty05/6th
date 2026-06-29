// frontend/src/services/permissionService.js

import api from './api'
import authService from './auth'

class PermissionService {
  constructor() {
    this.permissions = null
    this.userRole = null
    this.loaded = false
    this.loadingPromise = null
  }

  async loadPermissions() {
    // If already loading, return the existing promise
    if (this.loadingPromise) {
      return this.loadingPromise
    }

    // If already loaded, return
    if (this.loaded) {
      return true
    }

    this.loadingPromise = (async () => {
      try {
        const response = await api.get('/debug/permissions')
        this.permissions = response.data.permissions
        this.userRole = response.data.role
        this.loaded = true
        console.log('✅ Permissions loaded:', this.userRole, this.permissions)
        return true
      } catch (error) {
        console.error('Failed to load permissions:', error)
        this.loaded = false
        return false
      } finally {
        this.loadingPromise = null
      }
    })()

    return this.loadingPromise
  }

  can(resource, action = 'read') {
    // Super admin can do everything
    if (this.userRole === 'super_admin') {
      return true
    }
    
    if (!this.permissions || !this.permissions[resource]) {
      return false
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

  // Tour Packages
  canViewTours() { return this.canView('tours') }
  canCreateTours() { return this.canCreate('tours') }
  canUpdateTours() { return this.canUpdate('tours') }
  canDeleteTours() { return this.canDelete('tours') }

  // Tour Bookings
  canViewBookings() { return this.canView('bookings') }
  canCreateBookings() { return this.canCreate('bookings') }
  canUpdateBookings() { return this.canUpdate('bookings') }
  canDeleteBookings() { return this.canDelete('bookings') }
  canApproveBookings() { return this.can('bookings', 'approve') }
  canRejectBookings() { return this.can('bookings', 'reject') }

  // Tour Availability
  canViewAvailability() { return this.canView('tours') }
  canUpdateAvailability() { return this.canUpdate('tours') }

  // Tour Settings
  canViewTourSettings() { return this.canView('tour_settings') }
  canUpdateTourSettings() { return this.canUpdate('tour_settings') }

  // ============================================================
  // COMPOSITE CHECKS
  // ============================================================

  /**
   * Check if user can manage tours (create, update, delete packages)
   * This is used in Dashboard.vue and AdminSidebar.vue
   */
  canManageTours() {
    return this.canCreateTours() || this.canUpdateTours() || this.canDeleteTours()
  }

  /**
   * Check if user can manage bookings (approve, reject, update)
   */
  canManageBookings() {
    return this.canApproveBookings() || this.canRejectBookings() || this.canUpdateBookings()
  }

  /**
   * Check if user can view tour data (read-only access)
   */
  canViewTourData() {
    return this.canViewTours() || this.canViewBookings()
  }

  /**
   * Check if user is a tour staff (manager or assistant)
   */
  isTourStaff() {
    return this.canViewTourData()
  }

  // ============================================================
  // DEBUG METHOD
  // ============================================================

  debugPermissions() {
    console.log('🔍 Permission Debug:')
    console.log('  Loaded:', this.loaded)
    console.log('  User Role:', this.userRole)
    console.log('  Permissions:', this.permissions)
    console.log('  Can View Tours:', this.canViewTours())
    console.log('  Can Manage Tours:', this.canManageTours())
    console.log('  Can View Bookings:', this.canViewBookings())
    console.log('  Can Approve Bookings:', this.canApproveBookings())
  }
}

// Create instance and auto-load
const permissionService = new PermissionService()

// Auto-load permissions on creation
permissionService.loadPermissions().then(success => {
  if (success) {
    console.log('✅ Permissions auto-loaded successfully')
  } else {
    console.warn('⚠️ Failed to auto-load permissions')
  }
})

export default permissionService