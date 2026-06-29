
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

  async loginStep1(email, password) {
    const response = await authAxios.post(`${API_URL}/auth/login/step1`, {
      email,
      password
    })
    return response.data
  }

  async loginStep2(otpCode, remember = false) {
    const response = await authAxios.post(`${API_URL}/auth/login/step2`, {
      otp_code: otpCode,
      remember
    })

    if (response.data.user) {
      this.setUser(response.data.user)
    }

    return response.data
  }

  async register(email, fullName, password) {
    const response = await authAxios.post(`${API_URL}/auth/register`, {
      email,
      full_name: fullName,
      password
    })
    return response.data
  }

  async forgotPassword(email) {
    const response = await authAxios.post(`${API_URL}/auth/forgot-password`, {
      email
    })
    return response.data
  }

  async resetPassword(token, newPassword) {
    const response = await authAxios.post(`${API_URL}/auth/reset-password`, {
      token,
      new_password: newPassword
    })
    return response.data
  }

  async logout() {
    await authAxios.post(`${API_URL}/auth/logout`)
    this.clearUser()
  }

  async getProfile() {
    const response = await authAxios.get(`${API_URL}/admin/profile`)
    return response.data
  }

  async updateProfile(fullName) {
    const response = await authAxios.put(`${API_URL}/admin/profile`, {
      full_name: fullName
    })
    if (response.data.user) {
      this.setUser(response.data.user)
    }
    return response.data
  }

  async changePassword(currentPassword, newPassword) {
    const response = await authAxios.put(`${API_URL}/admin/change-password`, {
      current_password: currentPassword,
      new_password: newPassword
    })
    return response.data
  }

  async checkAuth() {
    try {
      const response = await authAxios.get(`${API_URL}/admin/check-auth`)
      if (response.data.is_admin) {
        this.setUser(response.data.user)
        return true
      }
      return false
    } catch {
      return false
    }
  }

  // ============================================================
  // ROLE-BASED METHODS
  // ============================================================

  /**
   * Get the dashboard route based on user role

   */
  getRoleBasedDashboard() {
    const user = this.getUser()
    if (!user) return '/admin/login'
    

    console.log('User object for redirect:', user)
    // Super Admin → Admin Dashboard
    if (user.role === 'super_admin') {
      return '/admin/dashboard'
    }
    
    // Admin → Admin Dashboard
    if (user.role === 'admin') {
      return '/admin/dashboard'
    }
    
  // ✅ Tour Manager → Tour Manager Portal
  // Check BOTH role string AND flag
  if (user.is_tour_manager === true || user.role === 'tour_manager') {
    console.log('Redirecting to Tour Manager Portal')
    return '/tour-manager/dashboard'
  }
  
  // ✅ Tour Assistant → Tour Manager Portal (limited access)
  if (user.is_tour_assistant === true || user.role === 'tour_assistant') {
    console.log('Redirecting to Tour Assistant Portal')
    return '/tour-manager/dashboard'
  }
    
    // Partner → Partner Dashboard
    if (user.role === 'partner') {
      return '/partner/dashboard'
    }
    
    // Fallback
    return '/admin/dashboard'
  }

  /**
   * Get the redirect URL after login
   */
  getLoginRedirect() {
    return this.getRoleBasedDashboard()
  }

  /**
   * Get user role display name
   */
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
    
    // Check for flag-based roles first
    if (user.is_tour_manager === true) return 'Tour Manager'
    if (user.is_tour_assistant === true) return 'Tour Assistant'
    
    return roleMap[user.role] || user.role
  }

  /**
   * Check if user has specific role
   */
  hasRole(role) {
    const user = this.getUser()
    return user && user.role === role
  }

  /**
   * Check if user is super admin
   */
  isSuperAdmin() {
    return this.hasRole('super_admin')
  }

  /**
   * Check if user is admin (includes super admin)
   */
  isAdmin() {
    const user = this.getUser()
    return user && (user.role === 'super_admin' || user.role === 'admin')
  }

  /**
   * Check if user is a tour manager
   */
  isTourManager() {
    const user = this.getUser()
    return user && (user.is_tour_manager === true || user.role === 'tour_manager')
  }

  /**
   * Check if user is a tour assistant
   */
  isTourAssistant() {
    const user = this.getUser()
    return user && (user.is_tour_assistant === true || user.role === 'tour_assistant')
  }

  /**
   * Check if user has any tour-related role
   */
  isTourStaff() {
    const user = this.getUser()
    return user && (this.isTourManager() || this.isTourAssistant())
  }

  /**
   * Check if user is a partner
   */
  isPartner() {
    return this.hasRole('partner')
  }

  /**
   * Get user's access level
   */
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

  /**
   * Check if user can access the tour manager portal
   */
  canAccessTourPortal() {
    return this.isTourStaff()
  }

  /**
   * Check if user can manage tours (approve/reject bookings)
   */
  canManageTours() {
    const user = this.getUser()
    return user && (this.isTourManager() || user.role === 'admin' || user.role === 'super_admin')
  }

  /**
   * Check if user can assist with tours
   */
  canAssistTours() {
    const user = this.getUser()
    return user && (this.isTourAssistant() || this.isTourManager() || user.role === 'admin' || user.role === 'super_admin')
  }

  // ============================================================
  // USER DATA MANAGEMENT
  // ============================================================

  setUser(user) {
    this.user = user
    localStorage.setItem('user', JSON.stringify(user))
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
    localStorage.removeItem('auth_token')
  }

  isAuthenticated() {
    return !!this.getUser()
  }
}

export default new AuthService()