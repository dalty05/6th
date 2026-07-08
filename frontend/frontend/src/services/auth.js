import axios from 'axios'

const API_URL = '/api'

const authAxios = axios.create({
  withCredentials: true
})

class AuthService {
  constructor() {
    this.user = null
    this.loadUserFromStorage()
  }

  loadUserFromStorage() {
    const stored = localStorage.getItem('user')
    if (stored) {
      try {
        this.user = JSON.parse(stored)
      } catch (e) {
        this.user = null
      }
    }
  }

  // ============================================================
  // AUTHENTICATION METHODS
  // ============================================================

  async loginStep1(email, password) {
    try {
      const response = await authAxios.post(`${API_URL}/auth/login/step1`, {
        email,
        password
      })
      return response.data
    } catch (error) {
      console.error('Login step 1 error:', error)
      throw error
    }
  }

  async loginStep2(otpCode, remember = false) {
    try {
      const response = await authAxios.post(`${API_URL}/auth/login/step2`, {
        otp_code: otpCode,
        remember
      })

      if (response.data.user) {
        await this.setUserAndReload(response.data.user)
      }

      return response.data
    } catch (error) {
      console.error('Login step 2 error:', error)
      throw error
    }
  }

  async register(email, fullName, password) {
    try {
      const response = await authAxios.post(`${API_URL}/auth/register`, {
        email,
        full_name: fullName,
        password
      })
      return response.data
    } catch (error) {
      console.error('Registration error:', error)
      throw error
    }
  }

  async forgotPassword(email) {
    try {
      const response = await authAxios.post(`${API_URL}/auth/forgot-password`, {
        email
      })
      return response.data
    } catch (error) {
      console.error('Forgot password error:', error)
      throw error
    }
  }

  async resetPassword(token, newPassword) {
    try {
      const response = await authAxios.post(`${API_URL}/auth/reset-password`, {
        token,
        new_password: newPassword
      })
      return response.data
    } catch (error) {
      console.error('Reset password error:', error)
      throw error
    }
  }

  async logout() {
    try {
      await authAxios.post(`${API_URL}/auth/logout`)
    } catch (error) {
      console.warn('Logout request failed:', error)
    } finally {
      this.clearUser()
      await this.clearPermissions()
    }
  }

  // ============================================================
  // PROFILE METHODS
  // ============================================================

  async getProfile() {
    try {
      const response = await authAxios.get(`${API_URL}/admin/profile`)
      return response.data
    } catch (error) {
      console.error('Get profile error:', error)
      throw error
    }
  }

  async updateProfile(fullName) {
    try {
      const response = await authAxios.put(`${API_URL}/admin/profile`, {
        full_name: fullName
      })
      if (response.data.user) {
        await this.setUserAndReload(response.data.user)
      }
      return response.data
    } catch (error) {
      console.error('Update profile error:', error)
      throw error
    }
  }

  async changePassword(currentPassword, newPassword) {
    try {
      const response = await authAxios.put(`${API_URL}/admin/change-password`, {
        current_password: currentPassword,
        new_password: newPassword
      })
      return response.data
    } catch (error) {
      console.error('Change password error:', error)
      throw error
    }
  }

  async checkAuth() {
    try {
      const response = await authAxios.get(`${API_URL}/admin/check-auth`)
      console.debug('checkAuth response:', response.status, response.data)
      if (response.data.is_admin) {
        await this.setUserAndReload(response.data.user)
        return true
      }

      await this.clearUserAndPermissions()
      return false
    } catch (error) {
      console.warn('Auth check failed:', error)
      const status = error.response?.status
      console.debug('checkAuth error response:', status, error.response?.data)
      if (status === 401 || status === 403) {
        await this.clearUserAndPermissions()
      }
      return false
    }
  }

  // ============================================================
  // PERMISSION MANAGEMENT
  // ============================================================

  async loadPermissions() {
    try {
      const { default: permissionService } = await import('./permissionService')
      await permissionService.init()
      return true
    } catch (err) {
      console.warn('Failed to load permissions:', err)
      return false
    }
  }

  async clearPermissions() {
    try {
      const { default: permissionService } = await import('./permissionService')
      permissionService.clear()
    } catch (err) {
      console.warn('Failed to clear permission cache:', err)
    }
  }

  async refreshPermissions() {
    try {
      const { default: permissionService } = await import('./permissionService')
      permissionService.clear()
      await permissionService.init()
      return true
    } catch (err) {
      console.warn('Failed to refresh permissions:', err)
      return false
    }
  }

  // ============================================================
  // USER DATA MANAGEMENT
  // ============================================================

  setUser(user) {
    this.user = user
    localStorage.setItem('user', JSON.stringify(user))
  }

  async setUserAndReload(user) {
    this.setUser(user)
    await this.loadPermissions()
  }

  getUser() {
    if (!this.user) {
      const stored = localStorage.getItem('user')
      if (stored) {
        try {
          this.user = JSON.parse(stored)
        } catch (e) {
          this.user = null
        }
      }
    }
    return this.user
  }

  clearUser() {
    this.user = null
    localStorage.removeItem('user')
    localStorage.removeItem('user_permissions')
    
    // Remove auth headers
    delete axios.defaults.headers.common['Authorization']
    delete authAxios.defaults.headers.common['Authorization']
  }

  async clearUserAndPermissions() {
    this.clearUser()
    await this.clearPermissions()
  }

  isAuthenticated() {
    const user = this.getUser()
    return !!user
  }

  // ============================================================
  // ROLE-BASED METHODS
  // ============================================================

  getRoleBasedDashboard() {
    const user = this.getUser()
    if (!user) return '/admin/login'

    console.log('User object for redirect:', user)
    
    if (user.role === 'super_admin' || user.role === 'admin') {
      return '/admin/dashboard'
    }
    
    if (user.is_tour_manager === true || user.role === 'tour_manager') {
      console.log('Redirecting to Tour Manager Portal')
      return '/tour-manager/dashboard'
    }
    
    if (user.is_tour_assistant === true || user.role === 'tour_assistant') {
      console.log('Redirecting to Tour Assistant Portal')
      return '/tour-manager/dashboard'
    }
    
    if (user.role === 'partner') {
      return '/partner/dashboard'
    }
    
    return '/admin/dashboard'
  }

  getLoginRedirect() {
    return this.getRoleBasedDashboard()
  }

  getRoleDisplayName() {
    const user = this.getUser()
    if (!user) return ''
    
    const roleMap = {
      'super_admin': 'Super Administrator',
      'admin': 'Administrator',
      'tour_manager': 'Tour Manager',
      'tour_assistant': 'Tour Assistant',
      'partner': 'Marketing Partner'
    }
    
    if (user.is_tour_manager === true) return 'Tour Manager'
    if (user.is_tour_assistant === true) return 'Tour Assistant'
    
    return roleMap[user.role] || user.role
  }

  // ============================================================
  // ROLE CHECKS
  // ============================================================

  hasRole(role) {
    const user = this.getUser()
    return user && user.role === role
  }

  isSuperAdmin() {
    return this.hasRole('super_admin')
  }

  isAdmin() {
    const user = this.getUser()
    return user && (user.role === 'super_admin' || user.role === 'admin')
  }

  isTourManager() {
    const user = this.getUser()
    return user && (user.is_tour_manager === true || user.role === 'tour_manager')
  }

  isTourAssistant() {
    const user = this.getUser()
    return user && (user.is_tour_assistant === true || user.role === 'tour_assistant')
  }

  isTourStaff() {
    return this.isTourManager() || this.isTourAssistant()
  }

  isPartner() {
    return this.hasRole('partner')
  }

  getAccessLevel() {
    const user = this.getUser()
    if (!user) return null
    
    if (user.role === 'super_admin') return 'super_admin'
    if (user.role === 'admin') return 'admin'
    if (this.isTourManager()) return 'tour_manager'
    if (this.isTourAssistant()) return 'tour_assistant'
    if (user.role === 'partner') return 'partner'
    
    return 'user'
  }

  // ============================================================
  // PERMISSION HELPERS
  // ============================================================

  canAccessTourPortal() {
    return this.isTourStaff()
  }

  canManageTours() {
    const user = this.getUser()
    return user && (this.isTourManager() || this.isAdmin() || this.isSuperAdmin())
  }

  canAssistTours() {
    const user = this.getUser()
    return user && (this.isTourAssistant() || this.isTourManager() || this.isAdmin() || this.isSuperAdmin())
  }

  // ============================================================
  // SESSION MANAGEMENT
  // ============================================================

  // Removed refreshSession - using session-only auth

  // ============================================================
  // DEBUG
  // ============================================================

  debugAuth() {
    console.log('🔍 Auth Debug:')
    console.log('  Authenticated:', this.isAuthenticated())
    console.log('  User:', this.getUser())
    console.log('  Role:', this.getAccessLevel())
    console.log('  Dashboard:', this.getRoleBasedDashboard())
  }
}

// ✅ Create and export singleton instance
const authService = new AuthService()

// ❌ REMOVED: Token-related code since we're using session-only auth

export default authService