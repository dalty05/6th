// src/services/auth.js
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
      this.user = JSON.parse(stored)
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

  // ========== NEW: Role-Based Methods ==========
  
  /**
   * Get the dashboard route based on user role
   */
  getRoleBasedDashboard() {
    const user = this.getUser()
    if (!user) return '/admin/login'
    
    switch(user.role) {
      case 'super_admin':
        return '/admin/dashboard'
      case 'admin':
        return '/admin/dashboard'
      case 'partner':
        return '/partner/dashboard'
      default:
        return '/'
    }
  }

  /**
   * Get user role display name
   */
  getRoleDisplayName() {
    const user = this.getUser()
    if (!user) return ''
    
    switch(user.role) {
      case 'super_admin':
        return 'Super Administrator'
      case 'admin':
        return 'Administrator'
      case 'partner':
        return 'Marketing Partner'
      default:
        return user.role
    }
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
   * Check if user is partner
   */
  isPartner() {
    return this.hasRole('partner')
  }

  setUser(user) {
    this.user = user
    localStorage.setItem('user', JSON.stringify(user))
  }

  getUser() {
    if (!this.user) {
      const stored = localStorage.getItem('user')
      if (stored) {
        this.user = JSON.parse(stored)
      }
    }
    return this.user
  }

  clearUser() {
    this.user = null
    localStorage.removeItem('user')
    localStorage.removeItem('user_permissions')
  }

  isAuthenticated() {
    return !!this.getUser()
  }
}

export default new AuthService()