// frontend/src/services/permissionService.js
import api from './api'
import authService from './auth'

class PermissionService {
  constructor() {
    this.permissions = null
    this.userRole = null
  }

  async loadPermissions() {
    try {
      // Get current user's permissions from backend
      const response = await api.get('/debug/permissions')
      this.permissions = response.data.permissions
      this.userRole = response.data.role
      return true
    } catch (error) {
      console.error('Failed to load permissions:', error)
      return false
    }
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

  // Specific helper methods for common resources
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
  canViewSettings() { return this.canView('settings') }
  canUpdateSettings() { return this.canUpdate('settings') }

  canViewContacts() { return this.canView('contacts') }
  canUpdateContacts() { return this.canUpdate('contacts') }
  canDeleteContacts() { return this.canDelete('contacts') }

  canViewPermissions() { return this.userRole === 'super_admin' }
  canManagePermissions() { return this.userRole === 'super_admin' }
}

export default new PermissionService()