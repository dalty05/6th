import axios from 'axios'

const API_URL = '/api'

class AuthService {
  constructor() {
    this.user = null
  }

  async loginStep1(email, password) {
    const response = await axios.post(`${API_URL}/auth/login/step1`, {
      email,
      password
    })
    return response.data
  }

  async loginStep2(otpCode, remember = false) {
    const response = await axios.post(`${API_URL}/auth/login/step2`, {
      otp_code: otpCode,
      remember
    })
    
    if (response.data.user) {
      this.setUser(response.data.user)
    }
    return response.data
  }

  async register(email, fullName, password) {
    const response = await axios.post(`${API_URL}/auth/register`, {
      email,
      full_name: fullName,
      password
    })
    return response.data
  }

  async forgotPassword(email) {
    const response = await axios.post(`${API_URL}/auth/forgot-password`, {
      email
    })
    return response.data
  }

  async resetPassword(token, newPassword) {
    const response = await axios.post(`${API_URL}/auth/reset-password`, {
      token,
      new_password: newPassword
    })
    return response.data
  }

  async getUsers() {
    const response = await axios.get(`${API_URL}/admin/users`)
    return response.data
  }

  async approveUser(userId) {
    const response = await axios.put(`${API_URL}/admin/users/${userId}/approve`)
    return response.data
  }

  async suspendUser(userId, isActive, reason = '') {
    const response = await axios.put(`${API_URL}/admin/users/${userId}/suspend`, {
      is_active: isActive,
      reason
    })
    return response.data
  }

  async changeUserRole(userId, role) {
    const response = await axios.put(`${API_URL}/admin/users/${userId}/role`, {
      role
    })
    return response.data
  }

  async deleteUser(userId) {
    const response = await axios.delete(`${API_URL}/admin/users/${userId}`)
    return response.data
  }

  async logout() {
    await axios.post(`${API_URL}/auth/logout`)
    this.clearUser()
  }

  async checkAuth() {
    try {
      const response = await axios.get(`${API_URL}/admin/check-auth`)
      if (response.data.is_admin) {
        this.setUser(response.data.user)
        return true
      }
      return false
    } catch {
      return false
    }
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
  }

  isAuthenticated() {
    return !!this.getUser()
  }

  isSuperAdmin() {
    const user = this.getUser()
    return user && user.role === 'super_admin'
  }
}

export default new AuthService()